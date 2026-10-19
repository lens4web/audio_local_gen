import os
import time
import uuid
import soundfile as sf
import torch
import torchaudio
from pathlib import Path
from typing import Optional, Dict, Any, List

from app.config import SAMPLES_DIR, OUTPUTS_DIR, XTTS_MODEL_NAME

# Safe torchaudio.load patch for Apple Silicon without torchcodec
def _sf_load(filepath, **kwargs):
    data, sr = sf.read(filepath)
    tensor = torch.from_numpy(data).float()
    if tensor.ndim == 1:
        tensor = tensor.unsqueeze(0)
    else:
        tensor = tensor.t()
    return tensor, sr

torchaudio.load = _sf_load

# Safe torch.load patch for PyTorch 2.6+ weights_only default
_orig_torch_load = torch.load
def _safe_torch_load(*args, **kwargs):
    if "weights_only" not in kwargs:
        kwargs["weights_only"] = False
    return _orig_torch_load(*args, **kwargs)

torch.load = _safe_torch_load

class XTTSEngine:
    LANGUAGES = {
        "en": "English",
        "ru": "Russian",
        "es": "Spanish",
        "fr": "French",
        "de": "German",
        "it": "Italian",
        "pt": "Portuguese",
        "pl": "Polish",
        "tr": "Turkish",
        "nl": "Dutch",
        "cs": "Czech",
        "ar": "Arabic",
        "zh-cn": "Chinese",
        "ja": "Japanese",
        "hu": "Hungarian",
        "ko": "Korean",
        "hi": "Hindi",
    }

    def __init__(self):
        self.tts = None

    def is_available(self) -> bool:
        # Check if XTTS model is cached
        try:
            from TTS.api import TTS
            return True
        except ImportError:
            return False

    def load(self, use_gpu: bool = False):
        if self.tts is None:
            from TTS.api import TTS
            # On Apple Silicon CPU is most reliable and fast for XTTS
            self.tts = TTS(XTTS_MODEL_NAME, gpu=use_gpu)

    def synthesize(
        self,
        text: str,
        speaker_wav: str,
        language: str = "ru",
        temperature: float = 0.75,
        length_penalty: float = 1.0,
        repetition_penalty: float = 5.0,
        top_k: int = 50,
        top_p: float = 0.85,
        speed: float = 1.0,
    ) -> Dict[str, Any]:
        self.load(use_gpu=False)

        # Resolve speaker_wav path
        ref_path = Path(speaker_wav)
        if not ref_path.is_absolute():
            ref_path = SAMPLES_DIR / speaker_wav

        if not ref_path.exists():
            raise FileNotFoundError(f"Reference voice audio file not found: {ref_path}")

        start_time = time.time()
        filename = f"xtts_{uuid.uuid4().hex[:8]}.wav"
        output_path = OUTPUTS_DIR / filename

        self.tts.tts_to_file(
            text=text,
            speaker_wav=str(ref_path),
            language=language,
            file_path=str(output_path),
            temperature=temperature,
            length_penalty=length_penalty,
            repetition_penalty=repetition_penalty,
            top_k=top_k,
            top_p=top_p,
            speed=speed,
        )

        elapsed = time.time() - start_time

        # Read back WAV to inspect duration
        data, rate = sf.read(str(output_path))
        duration = len(data) / rate

        return {
            "model": "xtts-v2",
            "filename": filename,
            "url": f"/api/audio/{filename}",
            "duration": round(duration, 2),
            "sample_rate": rate,
            "elapsed_time": round(elapsed, 2),
            "rtf": round(elapsed / duration, 3) if duration > 0 else 0,
            "parameters": {
                "reference_voice": ref_path.name,
                "language": language,
                "temperature": temperature,
                "length_penalty": length_penalty,
                "repetition_penalty": repetition_penalty,
                "top_k": top_k,
                "top_p": top_p,
                "speed": speed,
            }
        }
