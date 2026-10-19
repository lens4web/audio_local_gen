#!/usr/bin/env python3
import sys
import argparse
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import (
    KOKORO_MODEL_URL, KOKORO_VOICES_URL, KOKORO_MODEL_PATH, KOKORO_VOICES_PATH,
    PIPER_DIR, PIPER_VOICES,
    SILERO_DIR, SILERO_V4_URL, SILERO_V4_PATH, SILERO_V5_URL, SILERO_V5_PATH,
    SILERO_EN_URL, SILERO_EN_PATH,
    XTTS_DIR, XTTS_MODEL_NAME, SAMPLES_DIR
)
from app.downloader import download_file

def download_kokoro():
    print("=== Downloading Kokoro-82M ONNX model and voices ===")
    if not KOKORO_MODEL_PATH.exists():
        download_file(KOKORO_MODEL_URL, KOKORO_MODEL_PATH, "Kokoro ONNX Model")
    else:
        print(f"Kokoro model already exists at {KOKORO_MODEL_PATH}")

    if not KOKORO_VOICES_PATH.exists():
        download_file(KOKORO_VOICES_URL, KOKORO_VOICES_PATH, "Kokoro Voices")
    else:
        print(f"Kokoro voices already exist at {KOKORO_VOICES_PATH}")

def download_piper(voices=None):
    print("=== Downloading Piper Voices ===")
    PIPER_DIR.mkdir(parents=True, exist_ok=True)
    selected = voices if voices else list(PIPER_VOICES.keys())
    for voice_id in selected:
        if voice_id not in PIPER_VOICES:
            print(f"Unknown voice: {voice_id}")
            continue
        info = PIPER_VOICES[voice_id]
        onnx_path = PIPER_DIR / f"{voice_id}.onnx"
        json_path = PIPER_DIR / f"{voice_id}.onnx.json"
        
        if not onnx_path.exists():
            download_file(info["onnx_url"], onnx_path, f"Piper {voice_id}.onnx")
        else:
            print(f"Piper model {onnx_path.name} already exists")
            
        if not json_path.exists():
            download_file(info["json_url"], json_path, f"Piper {voice_id}.onnx.json")
        else:
            print(f"Piper config {json_path.name} already exists")

def download_silero():
    print("=== Downloading Silero TTS models ===")
    SILERO_DIR.mkdir(parents=True, exist_ok=True)
    if not SILERO_V4_PATH.exists():
        download_file(SILERO_V4_URL, SILERO_V4_PATH, "Silero v4 Russian (40MB)")
    else:
        print(f"Silero v4 already exists at {SILERO_V4_PATH}")

    if not SILERO_V5_PATH.exists():
        download_file(SILERO_V5_URL, SILERO_V5_PATH, "Silero v5 Russian (145MB)")
    else:
        print(f"Silero v5 already exists at {SILERO_V5_PATH}")

    if not SILERO_EN_PATH.exists():
        download_file(SILERO_EN_URL, SILERO_EN_PATH, "Silero v3 English (57MB)")
    else:
        print(f"Silero English already exists at {SILERO_EN_PATH}")

def download_xtts():
    print("=== Downloading Coqui XTTS-v2 weights into local cache ===")
    try:
        from TTS.api import TTS
        print(f"Initializing XTTS-v2 ({XTTS_MODEL_NAME}). This may take a few minutes...")
        _ = TTS(XTTS_MODEL_NAME, gpu=False)
        print("XTTS-v2 model downloaded and verified successfully!")
    except Exception as e:
        print(f"Error downloading XTTS-v2: {e}")

def main():
    parser = argparse.ArgumentParser(description="Download voice models for Local Audio Combine")
    parser.add_argument("--model", choices=["all", "kokoro", "piper", "silero", "xtts"], default="all",
                        help="Which model to download (default: all)")
    args = parser.parse_args()

    if args.model in ("all", "kokoro"):
        download_kokoro()
    if args.model in ("all", "piper"):
        # Download all 6 piper voices
        download_piper(list(PIPER_VOICES.keys()))
    if args.model in ("all", "silero"):
        download_silero()
    if args.model in ("all", "xtts"):
        download_xtts()

    print("\n[Done] All requested models are ready.")

if __name__ == "__main__":
    main()
