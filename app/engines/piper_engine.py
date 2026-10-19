import os
import time
import uuid
import wave
from pathlib import Path
from typing import Optional, Dict, Any, List

from app.config import PIPER_DIR, PIPER_VOICES, OUTPUTS_DIR

class PiperEngine:
    def __init__(self):
        self.loaded_voices: Dict[str, Any] = {}

    def get_available_voices(self) -> List[Dict[str, Any]]:
        voices = []
        for voice_id, meta in PIPER_VOICES.items():
            onnx_path = PIPER_DIR / f"{voice_id}.onnx"
            json_path = PIPER_DIR / f"{voice_id}.onnx.json"
            is_installed = onnx_path.exists() and json_path.exists()
            voices.append({
                "id": voice_id,
                "name": meta["name"],
                "language": meta["language"],
                "installed": is_installed,
            })
        return voices

    def is_available(self) -> bool:
        # At least one piper voice installed
        for v in self.get_available_voices():
            if v["installed"]:
                return True
        return False

    def load_voice(self, voice_id: str):
        if voice_id not in self.loaded_voices:
            onnx_path = PIPER_DIR / f"{voice_id}.onnx"
            json_path = PIPER_DIR / f"{voice_id}.onnx.json"
            if not (onnx_path.exists() and json_path.exists()):
                raise FileNotFoundError(f"Piper voice {voice_id} is not downloaded yet.")
            from piper import PiperVoice
            self.loaded_voices[voice_id] = PiperVoice.load(str(onnx_path), config_path=str(json_path))
        return self.loaded_voices[voice_id]

    def synthesize(
        self,
        text: str,
        voice_id: str = "ru_RU-denis-medium",
        speed: float = 1.0,
        noise_scale: float = 0.667,
        noise_w_scale: float = 0.8,
    ) -> Dict[str, Any]:
        voice = self.load_voice(voice_id)

        from piper.config import SynthesisConfig
        # Speed in Piper: length_scale. length_scale < 1.0 means faster, > 1.0 means slower.
        length_scale = 1.0 / max(speed, 0.2)
        syn_config = SynthesisConfig(
            length_scale=length_scale,
            noise_scale=noise_scale,
            noise_w_scale=noise_w_scale,
        )

        start_time = time.time()
        filename = f"piper_{uuid.uuid4().hex[:8]}.wav"
        output_path = OUTPUTS_DIR / filename

        with wave.open(str(output_path), "wb") as wav_file:
            voice.synthesize_wav(text, wav_file, syn_config=syn_config)

        elapsed = time.time() - start_time

        # Read back WAV to inspect duration and sample rate
        with wave.open(str(output_path), "rb") as wf:
            frames = wf.getnframes()
            rate = wf.getframerate()
            duration = frames / float(rate)

        return {
            "model": "piper",
            "filename": filename,
            "url": f"/api/audio/{filename}",
            "duration": round(duration, 2),
            "sample_rate": rate,
            "elapsed_time": round(elapsed, 2),
            "rtf": round(elapsed / duration, 3) if duration > 0 else 0,
            "parameters": {
                "voice_id": voice_id,
                "speed": speed,
                "noise_scale": noise_scale,
                "noise_w_scale": noise_w_scale,
            }
        }
