import os
from pathlib import Path

# Base Paths (Strictly within project folder)
BASE_DIR = Path(__file__).resolve().parent.parent
MODELS_DIR = BASE_DIR / "models"
SAMPLES_DIR = BASE_DIR / "samples"
OUTPUTS_DIR = BASE_DIR / "outputs"
CACHE_DIR = BASE_DIR / "cache"
STATIC_DIR = BASE_DIR / "static"

# Local Cache overrides to prevent writing to ~/.cache or outside directories
HF_CACHE_DIR = CACHE_DIR / "huggingface"
TORCH_CACHE_DIR = CACHE_DIR / "torch"
PIPER_CACHE_DIR = CACHE_DIR / "piper"

for dir_path in [MODELS_DIR, SAMPLES_DIR, OUTPUTS_DIR, CACHE_DIR, HF_CACHE_DIR, TORCH_CACHE_DIR, PIPER_CACHE_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# Set environment variables for huggingface, torch, and coqui TOS
os.environ["HF_HOME"] = str(HF_CACHE_DIR)
os.environ["TORCH_HOME"] = str(TORCH_CACHE_DIR)
os.environ["PIPER_CACHE_DIR"] = str(PIPER_CACHE_DIR)
os.environ["COQUI_TOS_AGREED"] = "1"

# Kokoro Configuration
KOKORO_MODEL_URL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx"
KOKORO_VOICES_URL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin"
KOKORO_DIR = MODELS_DIR / "kokoro"
KOKORO_MODEL_PATH = KOKORO_DIR / "kokoro-v1.0.onnx"
KOKORO_VOICES_PATH = KOKORO_DIR / "voices-v1.0.bin"

# Piper Configuration
PIPER_DIR = MODELS_DIR / "piper"
PIPER_VOICES = {
    "ru_RU-denis-medium": {
        "name": "Denis (RU Male)",
        "language": "ru",
        "onnx_url": "https://huggingface.co/rhasspy/piper-voices/resolve/main/ru/ru_RU/denis/medium/ru_RU-denis-medium.onnx",
        "json_url": "https://huggingface.co/rhasspy/piper-voices/resolve/main/ru/ru_RU/denis/medium/ru_RU-denis-medium.onnx.json",
    },
    "ru_RU-ruslan-medium": {
        "name": "Ruslan (RU Male)",
        "language": "ru",
        "onnx_url": "https://huggingface.co/rhasspy/piper-voices/resolve/main/ru/ru_RU/ruslan/medium/ru_RU-ruslan-medium.onnx",
        "json_url": "https://huggingface.co/rhasspy/piper-voices/resolve/main/ru/ru_RU/ruslan/medium/ru_RU-ruslan-medium.onnx.json",
    },
    "ru_RU-dmitri-medium": {
        "name": "Dmitri (RU Male)",
        "language": "ru",
        "onnx_url": "https://huggingface.co/rhasspy/piper-voices/resolve/main/ru/ru_RU/dmitri/medium/ru_RU-dmitri-medium.onnx",
        "json_url": "https://huggingface.co/rhasspy/piper-voices/resolve/main/ru/ru_RU/dmitri/medium/ru_RU-dmitri-medium.onnx.json",
    },
    "ru_RU-irina-medium": {
        "name": "Irina (RU Female)",
        "language": "ru",
        "onnx_url": "https://huggingface.co/rhasspy/piper-voices/resolve/main/ru/ru_RU/irina/medium/ru_RU-irina-medium.onnx",
        "json_url": "https://huggingface.co/rhasspy/piper-voices/resolve/main/ru/ru_RU/irina/medium/ru_RU-irina-medium.onnx.json",
    },
    "en_US-lessac-medium": {
        "name": "Lessac (EN Female)",
        "language": "en",
        "onnx_url": "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx",
        "json_url": "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json",
    },
    "en_US-ryan-medium": {
        "name": "Ryan (EN Male)",
        "language": "en",
        "onnx_url": "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/ryan/medium/en_US-ryan-medium.onnx",
        "json_url": "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/ryan/medium/en_US-ryan-medium.onnx.json",
    }
}

# Silero Configuration
SILERO_DIR = MODELS_DIR / "silero"
SILERO_V4_URL = "https://models.silero.ai/models/tts/ru/v4_ru.pt"
SILERO_V5_URL = "https://models.silero.ai/models/tts/ru/v5_ru.pt"
SILERO_EN_URL = "https://models.silero.ai/models/tts/en/v3_en.pt"
SILERO_V4_PATH = SILERO_DIR / "v4_ru.pt"
SILERO_V5_PATH = SILERO_DIR / "v5_ru.pt"
SILERO_EN_PATH = SILERO_DIR / "v3_en.pt"

# XTTS-v2 Configuration
XTTS_DIR = MODELS_DIR / "xtts"
XTTS_MODEL_NAME = "tts_models/multilingual/multi-dataset/xtts_v2"
