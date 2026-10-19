import os
import json
import time
import shutil
import platform
import psutil
from pathlib import Path
from typing import Dict, Any, List, Optional

from app.config import (
    BASE_DIR, MODELS_DIR, SAMPLES_DIR, OUTPUTS_DIR,
    KOKORO_DIR, PIPER_DIR, SILERO_DIR, XTTS_DIR
)
from app.engines.kokoro_engine import KokoroEngine
from app.engines.piper_engine import PiperEngine
from app.engines.silero_engine import SileroEngine
from app.engines.xtts_engine import XTTSEngine
from app.engines.fish_engine import FishSpeechEngine

HISTORY_FILE = OUTPUTS_DIR / "history.json"

class ModelManager:
    def __init__(self):
        self.kokoro = KokoroEngine()
        self.piper = PiperEngine()
        self.silero = SileroEngine()
        self.xtts = XTTSEngine()
        self.fish = FishSpeechEngine()
        self._init_history()

    def _init_history(self):
        if not HISTORY_FILE.exists():
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump([], f)

    def get_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        try:
            if HISTORY_FILE.exists():
                with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                    history = json.load(f)
                    return history[:limit]
        except Exception:
            pass
        return []

    def add_history(self, entry: Dict[str, Any]):
        try:
            history = self.get_history(limit=200)
            entry["timestamp"] = time.time()
            entry["formatted_date"] = time.strftime("%Y-%m-%d %H:%M:%S")
            history.insert(0, entry)
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump(history[:100], f, indent=2)
        except Exception as e:
            print(f"Error saving history: {e}")

    def get_hardware_info(self) -> Dict[str, Any]:
        mem = psutil.virtual_memory()
        disk = shutil.disk_usage(BASE_DIR)
        
        # Check MPS
        mps_available = False
        try:
            import torch
            mps_available = torch.backends.mps.is_available()
        except Exception:
            pass

        return {
            "os": f"{platform.system()} {platform.release()}",
            "arch": platform.machine(),
            "cpu_count": psutil.cpu_count(logical=True),
            "ram_total_gb": round(mem.total / (1024**3), 1),
            "ram_available_gb": round(mem.available / (1024**3), 1),
            "ram_percent": mem.percent,
            "mps_available": mps_available,
            "project_disk_free_gb": round(disk.free / (1024**3), 1),
        }

    def list_samples(self) -> List[Dict[str, Any]]:
        samples = []
        for file in SAMPLES_DIR.glob("*.wav"):
            samples.append({
                "filename": file.name,
                "path": str(file),
                "size_kb": round(file.stat().st_size / 1024, 1),
            })
        for file in (SAMPLES_DIR / "uploads").glob("*.wav"):
            samples.append({
                "filename": f"uploads/{file.name}",
                "path": str(file),
                "size_kb": round(file.stat().st_size / 1024, 1),
            })
        return samples

    def get_models_status(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": "kokoro-82m",
                "name": "Kokoro-82M",
                "tagline": "Ultralight ONNX Engine (82M params)",
                "description": "High quality English & multi-lingual TTS with voice mixing, phoneme control, and sub-second generation.",
                "installed": self.kokoro.is_available(),
                "languages": list(KokoroEngine.LANG_MAP.keys()),
                "language_names": KokoroEngine.LANG_MAP,
                "voices": KokoroEngine.VOICES,
                "supports_voice_clone": False,
                "supports_voice_mixing": True,
                "supports_emotion_tags": False,
                "supports_accents": False,
                "default_voice": "af_bella",
            },
            {
                "id": "piper",
                "name": "Piper TTS",
                "tagline": "Ultra-Fast Neural Voice Engine",
                "description": "Optimized ONNX architecture with Russian voices (Denis, Ruslan, Dmitri, Irina) and high speed on CPU.",
                "installed": self.piper.is_available(),
                "voices": self.piper.get_available_voices(),
                "supports_voice_clone": False,
                "supports_voice_mixing": False,
                "supports_emotion_tags": False,
                "supports_accents": False,
                "default_voice": "ru_RU-denis-medium",
            },
            {
                "id": "silero",
                "name": "Silero TTS v4/v5",
                "tagline": "Russian Accent & Dual Language Engine",
                "description": "Native Russian pronunciation with explicit stress control ('+' sign before vowel), RUAccent dictionary, and English fallback.",
                "installed": self.silero.is_available(),
                "voices": {**SileroEngine.RU_SPEAKERS, **SileroEngine.EN_SPEAKERS},
                "sample_rates": SileroEngine.SAMPLE_RATES,
                "supports_voice_clone": False,
                "supports_voice_mixing": False,
                "supports_emotion_tags": False,
                "supports_accents": True,
                "default_voice": "aidar",
            },
            {
                "id": "xtts-v2",
                "name": "Coqui XTTS-v2",
                "tagline": "Few-Shot Voice Cloning (17 Languages)",
                "description": "Clone any voice from a 6-10 second reference audio. Supports Russian, English, Spanish, French, German, and 12 more.",
                "installed": self.xtts.is_available(),
                "languages": XTTSEngine.LANGUAGES,
                "supports_voice_clone": True,
                "supports_voice_mixing": False,
                "supports_emotion_tags": False,
                "supports_accents": False,
                "default_language": "ru",
            },
            {
                "id": "fish-speech",
                "name": "Fish Speech / OpenAudio S1-mini",
                "tagline": "Emotional Expressions & Voice Styling",
                "description": "Zero-shot cloning with emotion tags: (happy), (whispering), (sad), (angry), (excited), (calm).",
                "installed": self.fish.is_available(),
                "emotions": FishSpeechEngine.EMOTIONS,
                "supports_voice_clone": True,
                "supports_voice_mixing": False,
                "supports_emotion_tags": True,
                "supports_accents": False,
                "default_emotion": "(happy)",
            }
        ]

    def synthesize(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        model_id = payload.get("model", "kokoro-82m")
        text = payload.get("text", "").strip()
        if not text:
            raise ValueError("Input text cannot be empty.")

        if model_id == "kokoro-82m":
            result = self.kokoro.synthesize(
                text=text,
                voice=payload.get("voice", "af_bella"),
                speed=float(payload.get("speed", 1.0)),
                lang=payload.get("lang", "en-us"),
                blend_voice=payload.get("blend_voice"),
                blend_ratio=float(payload.get("blend_ratio", 0.5)),
            )
        elif model_id == "piper":
            result = self.piper.synthesize(
                text=text,
                voice_id=payload.get("voice_id", "ru_RU-denis-medium"),
                speed=float(payload.get("speed", 1.0)),
                noise_scale=float(payload.get("noise_scale", 0.667)),
                noise_w_scale=float(payload.get("noise_w_scale", 0.8)),
            )
        elif model_id == "silero":
            result = self.silero.synthesize(
                text=text,
                speaker=payload.get("speaker", "aidar"),
                sample_rate=int(payload.get("sample_rate", 48000)),
                auto_accent=bool(payload.get("auto_accent", True)),
                speed=float(payload.get("speed", 1.0)),
            )
        elif model_id == "xtts-v2":
            result = self.xtts.synthesize(
                text=text,
                speaker_wav=payload.get("speaker_wav", "demo_female_en.wav"),
                language=payload.get("language", "ru"),
                temperature=float(payload.get("temperature", 0.75)),
                length_penalty=float(payload.get("length_penalty", 1.0)),
                repetition_penalty=float(payload.get("repetition_penalty", 5.0)),
                top_k=int(payload.get("top_k", 50)),
                top_p=float(payload.get("top_p", 0.85)),
                speed=float(payload.get("speed", 1.0)),
            )
        elif model_id == "fish-speech":
            result = self.fish.synthesize(
                text=text,
                speaker_wav=payload.get("speaker_wav"),
                temperature=float(payload.get("temperature", 0.7)),
                top_p=float(payload.get("top_p", 0.8)),
                repetition_penalty=float(payload.get("repetition_penalty", 1.2)),
                speed=float(payload.get("speed", 1.0)),
            )
        else:
            raise ValueError(f"Unknown model identifier: {model_id}")

        result["text"] = text
        self.add_history(result)
        return result
