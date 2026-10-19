import os
import re
import time
import uuid
import torch
import soundfile as sf
from pathlib import Path
from typing import Optional, Dict, Any, List

from app.config import SILERO_V4_PATH, SILERO_V5_PATH, SILERO_EN_PATH, OUTPUTS_DIR

class SileroEngine:
    RU_SPEAKERS = {
        "aidar": "Aidar (Male)",
        "baya": "Baya (Female)",
        "kseniya": "Kseniya (Female)",
        "xenia": "Xenia (Female)",
        "eugene": "Eugene (Male)",
        "random": "Random Voice",
    }

    EN_SPEAKERS = {
        "en_0": "English Female (en_0)",
        "en_1": "English Male (en_1)",
        "en_2": "English Female (en_2)",
        "en_3": "English Male (en_3)",
        "en_4": "English Female (en_4)",
    }

    SAMPLE_RATES = [48000, 24000, 8000]

    def __init__(self):
        self.ru_model = None
        self.en_model = None
        self.accentizer = None

    def is_available(self) -> bool:
        return SILERO_V4_PATH.exists() or SILERO_V5_PATH.exists() or SILERO_EN_PATH.exists()

    def load_ru_model(self):
        if self.ru_model is None:
            # Prefer v5 if available, fallback to v4
            model_path = SILERO_V5_PATH if SILERO_V5_PATH.exists() else SILERO_V4_PATH
            if not model_path.exists():
                raise FileNotFoundError("Silero Russian model file not found.")
            device = torch.device("cpu")
            self.ru_model = torch.package.PackageImporter(str(model_path)).load_pickle("tts_models", "model")
            self.ru_model.to(device)

    def load_en_model(self):
        if self.en_model is None:
            if not SILERO_EN_PATH.exists():
                raise FileNotFoundError("Silero English model file not found.")
            device = torch.device("cpu")
            self.en_model = torch.package.PackageImporter(str(SILERO_EN_PATH)).load_pickle("tts_models", "model")
            self.en_model.to(device)

    def load_accentizer(self):
        if self.accentizer is None:
            try:
                from ruaccent import RUAccent
                self.accentizer = RUAccent()
                self.accentizer.load(omograph_model_size="turbo", use_dictionary=True)
            except Exception as e:
                print(f"Warning: Could not load RUAccent: {e}")
                self.accentizer = None

    def process_accent(self, text: str) -> str:
        self.load_accentizer()
        if self.accentizer:
            try:
                return self.accentizer.process_all(text)
            except Exception as e:
                print(f"Warning: Accentizer error on text: {e}")
                return text
        return text

    def clean_text(self, text: str) -> str:
        # Strip emotion tags like (whispering), (happy), etc.
        text = re.sub(r"\([a-zA-Z\s_-]+\)", "", text)
        # Normalize punctuation & dashes
        text = text.replace("—", "–").replace("–", "-").replace("‑", "-")
        text = text.replace("“", "\"").replace("”", "\"").replace("«", "\"").replace("»", "\"")
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def has_cyrillic(self, text: str) -> bool:
        return bool(re.search(r"[а-яА-ЯёЁ]", text))

    def synthesize(
        self,
        text: str,
        speaker: str = "aidar",
        sample_rate: int = 48000,
        auto_accent: bool = True,
        speed: float = 1.0,
    ) -> Dict[str, Any]:
        cleaned = self.clean_text(text)
        if not cleaned:
            raise ValueError("Input text is empty or contains no valid characters.")

        is_cyrillic = self.has_cyrillic(cleaned)
        start_time = time.time()

        if is_cyrillic:
            self.load_ru_model()
            processed_text = cleaned
            if auto_accent and ("+" not in cleaned):
                processed_text = self.process_accent(cleaned)

            # Ensure valid Russian speaker
            ru_speaker = speaker if speaker in self.RU_SPEAKERS else "aidar"

            try:
                audio = self.ru_model.apply_tts(
                    text=processed_text,
                    speaker=ru_speaker,
                    sample_rate=sample_rate
                )
            except Exception as e:
                # If RU model failed, retry without accent marks
                clean_no_plus = processed_text.replace("+", "")
                audio = self.ru_model.apply_tts(
                    text=clean_no_plus,
                    speaker=ru_speaker,
                    sample_rate=sample_rate
                )
        else:
            # English / Latin text: auto-route to Silero English model
            if not SILERO_EN_PATH.exists():
                raise ValueError("Silero Russian model requires Cyrillic (Russian) text. Please input Russian text or switch to Kokoro-82M / XTTS for English.")
            
            self.load_en_model()
            processed_text = cleaned
            en_speaker = "en_0" if speaker not in self.EN_SPEAKERS else speaker

            audio = self.en_model.apply_tts(
                text=processed_text,
                speaker=en_speaker,
                sample_rate=sample_rate
            )

        audio_np = audio.numpy()

        # Handle speed alteration if requested
        if speed != 1.0 and abs(speed - 1.0) > 0.05:
            import scipy.signal
            num_samples = int(len(audio_np) / speed)
            audio_np = scipy.signal.resample(audio_np, num_samples)

        duration = len(audio_np) / sample_rate
        elapsed = time.time() - start_time

        filename = f"silero_{uuid.uuid4().hex[:8]}.wav"
        output_path = OUTPUTS_DIR / filename
        sf.write(str(output_path), audio_np, sample_rate)

        return {
            "model": "silero",
            "filename": filename,
            "url": f"/api/audio/{filename}",
            "duration": round(duration, 2),
            "sample_rate": sample_rate,
            "elapsed_time": round(elapsed, 2),
            "rtf": round(elapsed / duration, 3) if duration > 0 else 0,
            "processed_text": processed_text,
            "detected_language": "ru" if is_cyrillic else "en",
            "parameters": {
                "speaker": speaker,
                "sample_rate": sample_rate,
                "auto_accent": auto_accent,
                "speed": speed,
            }
        }
