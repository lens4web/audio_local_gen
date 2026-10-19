import os
import time
import uuid
import numpy as np
import soundfile as sf
from pathlib import Path
from typing import Optional, Dict, Any, List

from app.config import KOKORO_MODEL_PATH, KOKORO_VOICES_PATH, OUTPUTS_DIR

class KokoroEngine:
    VOICES = {
        # American English
        "af_heart": "American Heart (Female)",
        "af_alloy": "American Alloy (Female)",
        "af_aoede": "American Aoede (Female)",
        "af_bella": "American Bella (Female)",
        "af_jessica": "American Jessica (Female)",
        "af_kore": "American Kore (Female)",
        "af_nicole": "American Nicole (Female)",
        "af_nova": "American Nova (Female)",
        "af_river": "American River (Female)",
        "af_sarah": "American Sarah (Female)",
        "af_sky": "American Sky (Female)",
        "am_adam": "American Adam (Male)",
        "am_echo": "American Echo (Male)",
        "am_eric": "American Eric (Male)",
        "am_fenrir": "American Fenrir (Male)",
        "am_liam": "American Liam (Male)",
        "am_michael": "American Michael (Male)",
        "am_onyx": "American Onyx (Male)",
        "am_puck": "American Puck (Male)",
        "am_santa": "American Santa (Male)",
        # British English
        "bf_alice": "British Alice (Female)",
        "bf_emma": "British Emma (Female)",
        "bf_isabella": "British Isabella (Female)",
        "bf_lily": "British Lily (Female)",
        "bm_daniel": "British Daniel (Male)",
        "bm_fable": "British Fable (Male)",
        "bm_george": "British George (Male)",
        "bm_lewis": "British Lewis (Male)",
        # Japanese
        "jf_alpha": "Japanese Alpha (Female)",
        "jf_gongitsune": "Japanese Gongitsune (Female)",
        "jf_nezumi": "Japanese Nezumi (Female)",
        "jf_tebukuro": "Japanese Tebukuro (Female)",
        "jm_kumo": "Japanese Kumo (Male)",
        # Chinese
        "zf_xiaobei": "Chinese Xiaobei (Female)",
        "zf_xiaoni": "Chinese Xiaoni (Female)",
        "zf_xiaoxiao": "Chinese Xiaoxiao (Female)",
        "zf_xiaoyi": "Chinese Xiaoyi (Female)",
        "zm_yunjian": "Chinese Yunjian (Male)",
        "zm_yunxi": "Chinese Yunxi (Male)",
        "zm_yunxia": "Chinese Yunxia (Male)",
        "zm_yunyang": "Chinese Yunyang (Male)",
        # Spanish
        "ef_dora": "Spanish Dora (Female)",
        "em_alex": "Spanish Alex (Male)",
        "em_santa": "Spanish Santa (Male)",
        # French
        "ff_siwis": "French Siwis (Female)",
        # Hindi
        "hf_alpha": "Hindi Alpha (Female)",
        "hf_beta": "Hindi Beta (Female)",
        "hm_omega": "Hindi Omega (Male)",
        "hm_psi": "Hindi Psi (Male)",
        # Italian
        "if_sara": "Italian Sara (Female)",
        "im_nicola": "Italian Nicola (Male)",
        # Portuguese
        "pf_dora": "Portuguese Dora (Female)",
        "pm_alex": "Portuguese Alex (Male)",
        "pm_santa": "Portuguese Santa (Male)",
    }

    LANG_MAP = {
        "en-us": "English (US)",
        "en-gb": "English (UK)",
        "es": "Spanish",
        "fr": "French",
        "hi": "Hindi",
        "it": "Italian",
        "pt-br": "Portuguese (Brazil)",
        "ja": "Japanese",
        "zh": "Chinese",
    }

    def __init__(self):
        self.model = None

    def is_available(self) -> bool:
        return KOKORO_MODEL_PATH.exists() and KOKORO_VOICES_PATH.exists()

    def load(self):
        if self.model is None:
            if not self.is_available():
                raise FileNotFoundError("Kokoro model files not found. Please download them first.")
            from kokoro_onnx import Kokoro
            self.model = Kokoro(str(KOKORO_MODEL_PATH), str(KOKORO_VOICES_PATH))

    def synthesize(
        self,
        text: str,
        voice: str = "af_bella",
        speed: float = 1.0,
        lang: str = "en-us",
        blend_voice: Optional[str] = None,
        blend_ratio: float = 0.5,
    ) -> Dict[str, Any]:
        self.load()

        start_time = time.time()
        
        # Check if voice blending is requested
        if blend_voice and blend_voice in self.VOICES:
            v1 = self.model.get_voice_style(voice)
            v2 = self.model.get_voice_style(blend_voice)
            combined_voice = np.add(v1 * (1.0 - blend_ratio), v2 * blend_ratio)
            samples, sample_rate = self.model.create(
                text=text,
                voice=combined_voice,
                speed=float(speed),
                lang=lang
            )
        else:
            samples, sample_rate = self.model.create(
                text=text,
                voice=voice,
                speed=float(speed),
                lang=lang
            )

        duration = len(samples) / sample_rate
        elapsed = time.time() - start_time

        filename = f"kokoro_{uuid.uuid4().hex[:8]}.wav"
        output_path = OUTPUTS_DIR / filename
        sf.write(str(output_path), samples, sample_rate)

        return {
            "model": "kokoro-82m",
            "filename": filename,
            "url": f"/api/audio/{filename}",
            "duration": round(duration, 2),
            "sample_rate": sample_rate,
            "elapsed_time": round(elapsed, 2),
            "rtf": round(elapsed / duration, 3) if duration > 0 else 0,
            "parameters": {
                "voice": voice,
                "speed": speed,
                "lang": lang,
                "blend_voice": blend_voice,
                "blend_ratio": blend_ratio,
            }
        }
