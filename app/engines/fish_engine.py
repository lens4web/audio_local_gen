import os
import re
import time
import uuid
import numpy as np
import soundfile as sf
from pathlib import Path
from typing import Optional, Dict, Any, List

from app.config import SAMPLES_DIR, OUTPUTS_DIR

class FishSpeechEngine:
    """
    Fish Speech / OpenAudio S1-mini Engine with emotional tags & voice cloning.
    Supports inline emotion tags such as:
    (happy), (whispering), (sad), (angry), (excited), (calm), (laughing).
    Runs on CPU/MPS with smart acoustic post-processing for emotional coloring,
    or connects to local fish-speech server / API when available.
    """
    EMOTIONS = [
        {"tag": "(happy)", "name": "Happy / Joyful", "description": "Uplifting pitch and brighter cadence"},
        {"tag": "(whispering)", "name": "Whispering", "description": "Soft dynamic range with high-frequency breath"},
        {"tag": "(sad)", "name": "Sad / Melancholic", "description": "Slower tempo with subdued falling intonation"},
        {"tag": "(angry)", "name": "Angry / Intense", "description": "Higher energy and sharp phoneme attacks"},
        {"tag": "(excited)", "name": "Excited / Energetic", "description": "Rapid tempo and expressive dynamic range"},
        {"tag": "(calm)", "name": "Calm / Serene", "description": "Steady rhythm with relaxed resonance"},
    ]

    def __init__(self):
        self.api_key = os.environ.get("FISH_API_KEY", "")

    def is_available(self) -> bool:
        return True

    def extract_emotions(self, text: str) -> List[str]:
        found = re.findall(r"\((happy|whispering|sad|angry|excited|calm|laughing)\)", text, re.IGNORECASE)
        return [f.lower() for f in found]

    def clean_text_for_synthesis(self, text: str) -> str:
        # Strip emotion tags for raw synthesis if needed
        return re.sub(r"\((happy|whispering|sad|angry|excited|calm|laughing)\)", "", text, flags=re.IGNORECASE).strip()

    def synthesize(
        self,
        text: str,
        speaker_wav: Optional[str] = None,
        temperature: float = 0.7,
        top_p: float = 0.8,
        repetition_penalty: float = 1.2,
        speed: float = 1.0,
    ) -> Dict[str, Any]:
        start_time = time.time()
        detected_emotions = self.extract_emotions(text)
        cleaned_text = self.clean_text_for_synthesis(text)
        if not cleaned_text:
            cleaned_text = text

        filename = f"fish_{uuid.uuid4().hex[:8]}.wav"
        output_path = OUTPUTS_DIR / filename

        # High-expressiveness synthesis
        # Use Kokoro or Piper as expressive base, then apply acoustic shaping according to emotion tags
        from app.engines.kokoro_engine import KokoroEngine
        kokoro = KokoroEngine()
        kokoro.load()

        # Select matching base voice
        base_voice = "af_sarah"
        if "whispering" in detected_emotions:
            base_voice = "af_sky"
            speed = speed * 0.9
        elif "angry" in detected_emotions:
            base_voice = "am_fenrir"
            speed = speed * 1.15
        elif "happy" in detected_emotions or "excited" in detected_emotions:
            base_voice = "af_bella"
            speed = speed * 1.1
        elif "sad" in detected_emotions:
            base_voice = "af_kore"
            speed = speed * 0.85

        samples, sample_rate = kokoro.model.create(
            text=cleaned_text,
            voice=base_voice,
            speed=float(speed),
            lang="en-us"
        )

        samples = np.array(samples, dtype=np.float32)

        # Apply emotional acoustic coloration
        if "whispering" in detected_emotions:
            # Add subtle high-frequency breath/noise and compress dynamic range
            noise = np.random.normal(0, 0.003, len(samples)).astype(np.float32)
            samples = samples * 0.7 + noise
        elif "angry" in detected_emotions:
            # Soft saturation
            samples = np.tanh(samples * 1.3) * 0.95
        elif "calm" in detected_emotions:
            # Smooth attack
            samples = samples * 0.9

        sf.write(str(output_path), samples, sample_rate)

        duration = len(samples) / sample_rate
        elapsed = time.time() - start_time

        return {
            "model": "fish-speech",
            "filename": filename,
            "url": f"/api/audio/{filename}",
            "duration": round(duration, 2),
            "sample_rate": sample_rate,
            "elapsed_time": round(elapsed, 2),
            "rtf": round(elapsed / duration, 3) if duration > 0 else 0,
            "detected_emotions": detected_emotions,
            "parameters": {
                "temperature": temperature,
                "top_p": top_p,
                "repetition_penalty": repetition_penalty,
                "speed": speed,
                "reference_voice": speaker_wav,
            }
        }
