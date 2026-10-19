# 🎙️ OmniVoice Studio

> **Universal Local Neural TTS Combine & Browser Control Panel**  
> Unified synthesis workbench combining **Kokoro-82M**, **Piper**, **Silero TTS**, **Coqui XTTS-v2**, and **Fish Speech / OpenAudio S1-mini** with native Apple Silicon (M1 Pro) acceleration.

[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.14+-ee4c2c.svg?style=flat&logo=pytorch)](https://pytorch.org)
[![ONNX Runtime](https://img.shields.io/badge/ONNX_Runtime-1.31+-005CED.svg?style=flat)](https://onnxruntime.ai)
[![Platform](https://img.shields.io/badge/Platform-macOS_Apple_Silicon-black.svg?style=flat&logo=apple)](https://apple.com)
[![License](https://img.shields.io/badge/Project-Educational_Personal-blue.svg?style=flat)](#license)

---

## 🌟 Overview

**OmniVoice Studio** is a self-contained local speech synthesis station accessible directly through your web browser. It brings together the top open-source neural TTS models into a single modern dashboard, exposing all fine-grained controls, voice cloning capabilities, stress accentuation, voice mixing, and emotion tagging.

All dependencies, models, and cache files reside strictly within the project directory.

```
                          ┌─────────────────────────────────────┐
                          │    Browser Control Panel UI (SPA)   │
                          │   Dark Glassmorphism • Audio Player │
                          └──────────────────┬──────────────────┘
                                             │ HTTP REST / Streaming
                          ┌──────────────────▼──────────────────┐
                          │        FastAPI Unified Server       │
                          │        Hardware Telemetry & API     │
                          └──────────────────┬──────────────────┘
                                             │
      ┌────────────────┬─────────────────────┼─────────────────────┬─────────────────┐
      │                │                     │                     │                 │
┌─────▼───────┐  ┌─────▼───────┐      ┌──────▼───────┐      ┌──────▼───────┐   ┌─────▼───────┐
│ Kokoro-82M  │  │  Piper TTS  │      │  Silero TTS  │      │ Coqui XTTSv2 │   │ Fish Speech │
│ ONNX • 82M  │  │ ONNX • Fast │      │ PyTorch • RU │      │ Voice Clone  │   │ Emotion S1  │
│ Voice Mix   │  │ Denis/Ruslan│      │ RUAccent (+) │      │ 17 Languages │   │ Style Tags  │
└─────────────┘  └─────────────┘      └──────────────┘      └──────────────┘   └─────────────┘
```

---

## 📊 Model Comparison Matrix

| Model | Parameter Size / Weights | Russian Language | Voice Cloning | Key Capabilities | M1 Pro Performance |
| :--- | :--- | :---: | :---: | :--- | :--- |
| **Kokoro-82M** | 82M params (~330 MB) | ❌ (EN, JA, ZH, ES, FR, HI, IT, PT) | ❌ | Voice blending/mixing, speed scaling, sub-second latency | **Blazing fast** (<0.5s per sentence) |
| **Piper TTS** | 15–60 MB per voice | ✅ (Denis, Ruslan, Dmitri, Irina) + EN (Lessac, Ryan) | ❌ (Pre-trained) | Variable intonation (`noise_scale`), phoneme width (`noise_w`), 6 voices | **~15x faster than real-time** (RTF: 0.067) |
| **Silero TTS v4/v5** | ~40–145 MB | ✅ (Native Russian + English fallback) | ❌ | Explicit phonetic stress (`+`), automated homograph accenting via `RUAccent`, EN support | **Super fast** (RTF: ~0.48) |
| **Coqui XTTS-v2** | ~2 GB | ✅ (17 languages) | ✅ (6–10s audio sample) | In-browser microphone recorder & file upload, temperature, repetition penalty | **Real-time on CPU** (RTF: 1.48–1.76) |
| **Fish Speech** | ~0.5B params | ✅ | ✅ (Prompt reference) | Emotion tags: `(happy)`, `(whispering)`, `(sad)`, `(angry)`, `(excited)` | Real-time acoustic profile shaping |

---

## 🚀 Features

### 1. Unified Web Control Panel
- **Responsive Dark Glassmorphic Dashboard**: Built with modern CSS and Vanilla ES6 JavaScript (no heavy node_modules build step required).
- **System Telemetry**: Real-time monitoring of CPU cores, Apple Silicon architecture, 32GB RAM utilization, MPS acceleration status, and local disk space.
- **In-Browser Microphone Voice Cloning**: Record a 5–10 second voice clip right in your browser, upload it instantly, and clone it with XTTS-v2.
- **Audio Waveform & Player**: Integrated player with playback speed adjustment, duration reporting, Real-Time Factor (RTF) calculation, and one-click WAV download.
- **Generation History Drawer**: Replay previous syntheses, inspect exact parameters used, and export outputs.

### 2. Kokoro-82M (Ultralight & Multilingual)
- Supported voices:
  - **US English**: `af_heart`, `af_alloy`, `af_aoede`, `af_bella`, `af_jessica`, `af_kore`, `af_nicole`, `af_nova`, `af_river`, `af_sarah`, `af_sky`, `am_adam`, `am_echo`, `am_eric`, `am_fenrir`, `am_liam`, `am_michael`, `am_onyx`, `am_puck`, `am_santa`
  - **UK English**: `bf_alice`, `bf_emma`, `bf_isabella`, `bf_lily`, `bm_daniel`, `bm_fable`, `bm_george`, `bm_lewis`
  - **Japanese**: `jf_alpha`, `jf_gongitsune`, `jf_nezumi`, `jf_tebukuro`, `jm_kumo`
  - **Chinese**: `zf_xiaobei`, `zf_xiaoni`, `zf_xiaoxiao`, `zf_xiaoyi`, `zm_yunjian`, `zm_yunxi`, `zm_yunxia`, `zm_yunyang`
  - **Spanish, French, Hindi, Italian, Portuguese**
- **Voice Mixing**: Linear blending between two voice embedding vectors (e.g., 70% Bella + 30% Sarah).
- **Speed Control**: 0.5x to 2.0x.

### 3. Piper TTS (Ultra-Fast Russian & English)
- Integrated Russian voices: `ru_RU-denis-medium`, `ru_RU-ruslan-medium`, `ru_RU-dmitri-medium`, `ru_RU-irina-medium`.
- Integrated English voices: `en_US-lessac-medium`, `en_US-ryan-medium`.
- Fine-grained generation controls:
  - `length_scale` (Speech tempo)
  - `noise_scale` (Intonation variability)
  - `noise_w_scale` (Phoneme duration variance)

### 4. Silero TTS v4/v5 (Russian Stress, Homographs & Dual Language)
- Native Russian pronunciation with speakers: `aidar`, `baya`, `kseniya`, `xenia`, `eugene`, `random`.
- Built-in English model support with 119 speakers (`en_0` .. `en_118`).
- **Explicit Stress Control**: Add `+` before any vowel (e.g., `з+амок` [castle] vs `зам+ок` [door lock]).
- **Integrated RUAccent Engine**: Automatically resolves Russian homographs and places stress markers using transformer-based models.
- Sample rates: 48,000 Hz (HD), 24,000 Hz, 8,000 Hz.

### 5. Coqui XTTS-v2 (Zero-Shot Voice Cloning)
- 17 Supported Languages: Russian, English, Spanish, French, German, Italian, Portuguese, Polish, Turkish, Dutch, Czech, Arabic, Chinese, Japanese, Hungarian, Korean, Hindi.
- Uses any 6–10 second clean reference WAV/MP3.
- Parameter tuning: `temperature`, `length_penalty`, `repetition_penalty`, `top_k`, `top_p`, `speed`.
- Optimized with safe tensor loaders and C-based soundfile backend to eliminate Apple Silicon codec crashes.

### 6. Fish Speech / OpenAudio S1-mini (Emotion Tagging)
- Emotion tags supported directly in text:
  - `(happy)`: Joyful, uplifting intonation
  - `(whispering)`: High-frequency breath resonance, intimate dynamic range
  - `(sad)`: Melancholic falling cadence
  - `(angry)`: High energy with aggressive phoneme attacks
  - `(excited)`: Fast energetic tempo
  - `(calm)`: Serene, steady rhythm

---

## 🛠️ Quickstart

### 1. Requirements
- **Hardware**: macOS with Apple Silicon (M1 / M2 / M3 / M4, 16GB+ RAM recommended, 32GB optimal).
- **Software**: Python 3.11 or 3.10 installed (via Homebrew: `brew install python@3.11`).

### 2. One-Click Setup
Clone the repository and run the setup script:
```bash
git clone https://github.com/lens4web/audio_local_gen.git
cd audio_local_gen

# Run automated setup (creates .venv, installs packages, downloads base models)
chmod +x setup.sh run.sh
./setup.sh
```

### 3. Launching OmniVoice Studio
```bash
./run.sh
```
The server will start on `http://127.0.0.1:7860` and automatically open your default browser.

---

## 📁 Project Structure

All files, libraries, and caches remain strictly inside this folder:

```
audio_local_gen/
├── app/
│   ├── engines/
│   │   ├── fish_engine.py       # Fish Speech / emotion tag engine
│   │   ├── kokoro_engine.py     # Kokoro-82M ONNX engine & voice mixer
│   │   ├── piper_engine.py      # Piper TTS ONNX engine
│   │   ├── silero_engine.py     # Silero Russian TTS & RUAccent engine
│   │   └── xtts_engine.py       # Coqui XTTS-v2 voice cloning engine
│   ├── config.py                # Local paths, env overrides & URLs
│   ├── downloader.py            # Streaming downloader with progress tracking
│   ├── manager.py               # Unified model registry & hardware inspector
│   └── main.py                  # FastAPI REST API & static server
├── cache/                       # Local HF & Torch caches (no system pollution)
│   ├── huggingface/
│   ├── piper/
│   └── torch/
├── models/                      # Downloaded neural network weights
│   ├── kokoro/                  # kokoro-v1.0.onnx + voices-v1.0.bin
│   ├── piper/                   # ru_RU-denis, ru_RU-ruslan, en_US-lessac
│   ├── silero/                  # v4_ru.pt
│   └── xtts/                    # XTTS-v2 checkpoints
├── outputs/                     # Generated WAV audio files & history.json
├── samples/                     # Reference audio samples for voice cloning
│   ├── demo_female_en.wav       # Built-in reference voice (Female English)
│   ├── demo_male_ru.wav         # Built-in reference voice (Male Russian)
│   └── uploads/                 # User uploaded / mic recorded samples
├── scripts/
│   └── download_models.py       # CLI model downloader
├── static/
│   ├── app.js                   # Client-side UI controller
│   ├── index.html               # Main control panel SPA
│   └── style.css                # Glassmorphic dark styling
├── .gitignore                   # Keeps repository clean and lightweight
├── README.md                    # Project documentation
├── requirements.txt             # Verified Python dependencies
├── run.sh                       # One-click start script
└── setup.sh                     # One-click environment installer
```

---

## 📡 REST API Reference

The FastAPI backend exposes a clean REST API that can be consumed programmatically or integrated into other applications:

### `GET /api/system`
Returns host hardware and memory telemetry:
```json
{
  "os": "Darwin 25.6.0",
  "arch": "arm64",
  "cpu_count": 10,
  "ram_total_gb": 32.0,
  "ram_available_gb": 12.4,
  "mps_available": true,
  "project_disk_free_gb": 28.6
}
```

### `GET /api/models`
Returns all supported models, download status, voices, and capability flags.

### `POST /api/tts/generate`
Synthesizes speech using the selected model.

**Payload for Kokoro-82M:**
```json
{
  "model": "kokoro-82m",
  "text": "Hello world from Kokoro speech synthesis.",
  "voice": "af_bella",
  "speed": 1.0,
  "lang": "en-us",
  "blend_voice": "af_sarah",
  "blend_ratio": 0.3
}
```

**Payload for Piper TTS (Russian):**
```json
{
  "model": "piper",
  "text": "Привет! Пайпер синтезирует русскую речь.",
  "voice_id": "ru_RU-denis-medium",
  "speed": 1.0,
  "noise_scale": 0.667,
  "noise_w_scale": 0.8
}
```

**Payload for Silero TTS (Russian with Auto-Accenting):**
```json
{
  "model": "silero",
  "text": "Большой замок закрыт на замок.",
  "speaker": "aidar",
  "sample_rate": 48000,
  "auto_accent": true,
  "speed": 1.0
}
```

**Payload for XTTS-v2 Voice Cloning:**
```json
{
  "model": "xtts-v2",
  "text": "This voice has been cloned using Coqui XTTS.",
  "speaker_wav": "demo_female_en.wav",
  "language": "en",
  "temperature": 0.75,
  "repetition_penalty": 5.0,
  "speed": 1.0
}
```

**Payload for Fish Speech (Emotions):**
```json
{
  "model": "fish-speech",
  "text": "(whispering) This is a secret message delivered softly.",
  "speed": 1.0
}
```

### `POST /api/samples/upload`
Uploads a WAV, MP3, or FLAC reference audio file to `samples/uploads/` for voice cloning.

---

## ⚡ Apple Silicon (M1 Pro 32GB) Performance Notes

- **RAM**: With 32GB unified memory, all 5 models can be loaded into memory without swapping or OOM issues.
- **ONNX Acceleration**: Kokoro-82M and Piper utilize ONNX Runtime with optimized Apple Silicon NEON instructions, generating audio faster than real-time on CPU.
- **PyTorch MPS vs CPU**:
  - Silero TTS v4 executes in ~1 second on CPU.
  - XTTS-v2 executes reliably on CPU (~1.5x real-time factor) while avoiding known PyTorch MPS operator fallbacks.

---

## 🌐 Web Deployment Recommendations

To deploy this local studio to the web:
1. **Reverse Proxy**: Place **Nginx** or **Caddy** in front of Uvicorn on port `7860` with SSL certificates (Let's Encrypt).
2. **Authentication**: Add HTTP Basic Auth or OAuth2 middleware in `app/main.py`.
3. **Containerization**: Use `python:3.11-slim` with `ffmpeg` and `libsndfile1` installed.
4. **GPU Offloading**: On Linux servers with NVIDIA GPUs, set `use_gpu=True` in `xtts_engine.py` and install CUDA-enabled PyTorch for sub-second XTTS synthesis.

---

## 📄 License
This project is an educational personal laboratory integrating open-source speech research models. Model weights retain their respective upstream licenses.
