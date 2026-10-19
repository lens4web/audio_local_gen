import os
import shutil
import uuid
from pathlib import Path
from typing import Dict, Any, Optional

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.config import (
    BASE_DIR, STATIC_DIR, OUTPUTS_DIR, SAMPLES_DIR,
    PIPER_DIR, PIPER_VOICES, KOKORO_MODEL_PATH
)
from app.manager import ModelManager
from app.downloader import download_file

app = FastAPI(
    title="OmniVoice Studio - Local Unified TTS Combine",
    description="Unified local browser-based control panel for Kokoro-82M, Piper, Silero TTS, Coqui XTTS-v2, and Fish Speech.",
    version="1.0.0"
)

# Enable CORS for easy web integration in the future
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Model Manager
manager = ModelManager()

# Pydantic Request Models
class TTSRequest(BaseModel):
    model: str
    text: str
    # Kokoro params
    voice: Optional[str] = "af_bella"
    lang: Optional[str] = "en-us"
    blend_voice: Optional[str] = None
    blend_ratio: Optional[float] = 0.5
    # Piper params
    voice_id: Optional[str] = "ru_RU-denis-medium"
    noise_scale: Optional[float] = 0.667
    noise_w_scale: Optional[float] = 0.8
    # Silero params
    speaker: Optional[str] = "aidar"
    sample_rate: Optional[int] = 48000
    auto_accent: Optional[bool] = True
    # XTTS params
    speaker_wav: Optional[str] = "demo_female_en.wav"
    language: Optional[str] = "ru"
    temperature: Optional[float] = 0.75
    length_penalty: Optional[float] = 1.0
    repetition_penalty: Optional[float] = 5.0
    top_k: Optional[int] = 50
    top_p: Optional[float] = 0.85
    # General
    speed: Optional[float] = 1.0

class DownloadModelRequest(BaseModel):
    model_id: str
    sub_id: Optional[str] = None

# API Endpoints
@app.get("/api/system")
def get_system_info():
    return manager.get_hardware_info()

@app.get("/api/models")
def get_models():
    return {
        "models": manager.get_models_status()
    }

@app.get("/api/samples")
def get_samples():
    return {
        "samples": manager.list_samples()
    }

@app.get("/api/history")
def get_history(limit: int = 50):
    return {
        "history": manager.get_history(limit=limit)
    }

@app.post("/api/tts/generate")
def generate_speech(req: TTSRequest):
    try:
        result = manager.synthesize(req.model_dump())
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        error_msg = str(e).strip() or f"Synthesis failed ({type(e).__name__})"
        raise HTTPException(status_code=500, detail=error_msg)

@app.post("/api/samples/upload")
async def upload_sample(file: UploadFile = File(...)):
    try:
        upload_dir = SAMPLES_DIR / "uploads"
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in [".wav", ".mp3", ".ogg", ".m4a", ".flac"]:
            raise HTTPException(status_code=400, detail="Only audio files (.wav, .mp3, .ogg, .flac) are supported.")
        
        safe_name = f"ref_{uuid.uuid4().hex[:6]}_{Path(file.filename).name}"
        target_path = upload_dir / safe_name

        with open(target_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Convert to WAV if not wav
        if file_ext != ".wav":
            import soundfile as sf
            wav_path = target_path.with_suffix(".wav")
            data, sr = sf.read(str(target_path))
            sf.write(str(wav_path), data, sr)
            target_path.unlink()
            safe_name = wav_path.name
            target_path = wav_path

        return {
            "success": True,
            "filename": f"uploads/{safe_name}",
            "size_kb": round(target_path.stat().st_size / 1024, 1)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/audio/{filename}")
def get_audio(filename: str):
    file_path = OUTPUTS_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Audio file not found")
    return FileResponse(path=file_path, media_type="audio/wav", filename=filename)

@app.get("/api/samples/{filepath:path}")
def get_sample_audio(filepath: str):
    file_path = SAMPLES_DIR / filepath
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Sample audio file not found")
    return FileResponse(path=file_path, media_type="audio/wav", filename=file_path.name)

@app.post("/api/models/download")
def download_model(req: DownloadModelRequest, background_tasks: BackgroundTasks):
    from scripts.download_models import download_kokoro, download_piper, download_silero, download_xtts
    
    if req.model_id == "kokoro-82m":
        background_tasks.add_task(download_kokoro)
    elif req.model_id == "piper":
        voices = [req.sub_id] if req.sub_id else None
        background_tasks.add_task(download_piper, voices)
    elif req.model_id == "silero":
        background_tasks.add_task(download_silero)
    elif req.model_id == "xtts-v2":
        background_tasks.add_task(download_xtts)
    else:
        raise HTTPException(status_code=400, detail="Unknown model id")

    return {"success": True, "message": f"Downloading {req.model_id} in background."}

# Mount static files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/")
def read_root():
    return FileResponse(STATIC_DIR / "index.html")
