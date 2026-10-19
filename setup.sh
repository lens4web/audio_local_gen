#!/usr/bin/env bash
set -e

# Project root directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

echo "============================================================"
echo " OmniVoice Studio - Automated Local Environment Setup"
echo "============================================================"

# Ensure directories exist inside project
mkdir -p "$PROJECT_DIR/models/kokoro"
mkdir -p "$PROJECT_DIR/models/piper"
mkdir -p "$PROJECT_DIR/models/silero"
mkdir -p "$PROJECT_DIR/models/xtts"
mkdir -p "$PROJECT_DIR/samples/uploads"
mkdir -p "$PROJECT_DIR/outputs"
mkdir -p "$PROJECT_DIR/cache/huggingface"
mkdir -p "$PROJECT_DIR/cache/torch"
mkdir -p "$PROJECT_DIR/cache/piper"

# Export cache variables to guarantee no external directory pollution
export HF_HOME="$PROJECT_DIR/cache/huggingface"
export TORCH_HOME="$PROJECT_DIR/cache/torch"
export PIPER_CACHE_DIR="$PROJECT_DIR/cache/piper"
export COQUI_TOS_AGREED="1"

# Check Python version (prefer 3.11 or 3.10 for full ML compatibility)
PYTHON_BIN=""
if [ -x "/opt/homebrew/opt/python@3.11/bin/python3.11" ]; then
    PYTHON_BIN="/opt/homebrew/opt/python@3.11/bin/python3.11"
elif [ -x "/opt/homebrew/opt/python@3.10/bin/python3.10" ]; then
    PYTHON_BIN="/opt/homebrew/opt/python@3.10/bin/python3.10"
elif command -v python3.11 &> /dev/null; then
    PYTHON_BIN="python3.11"
elif command -v python3 &> /dev/null; then
    PYTHON_BIN="python3"
else
    echo "Error: Python 3 is required but was not found."
    exit 1
fi

echo "[*] Using Python: $($PYTHON_BIN --version)"

# Create local virtual environment if not present
if [ ! -d "$PROJECT_DIR/.venv" ]; then
    echo "[*] Creating local virtual environment in .venv..."
    $PYTHON_BIN -m venv "$PROJECT_DIR/.venv"
fi

echo "[*] Activating local virtual environment..."
source "$PROJECT_DIR/.venv/bin/activate"

echo "[*] Upgrading pip..."
pip install --upgrade pip

echo "[*] Installing Python dependencies from requirements.txt..."
pip install -r "$PROJECT_DIR/requirements.txt"

echo "[*] Pre-downloading essential models (Kokoro, Piper, Silero)..."
python "$PROJECT_DIR/scripts/download_models.py" --model all

echo "============================================================"
echo " Setup complete! Start the studio using: ./run.sh"
echo "============================================================"
