#!/usr/bin/env bash
set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

if [ ! -d "$PROJECT_DIR/.venv" ]; then
    echo "[!] Virtual environment not found. Running setup.sh first..."
    ./setup.sh
fi

source "$PROJECT_DIR/.venv/bin/activate"

# Strict local environment variable paths
export HF_HOME="$PROJECT_DIR/cache/huggingface"
export TORCH_HOME="$PROJECT_DIR/cache/torch"
export PIPER_CACHE_DIR="$PROJECT_DIR/cache/piper"
export COQUI_TOS_AGREED="1"

HOST="127.0.0.1"
PORT="7860"
URL="http://$HOST:$PORT"

echo "============================================================"
echo " Starting OmniVoice Studio on $URL"
echo "============================================================"

# Auto-open browser on macOS in background
(sleep 2 && open "$URL" 2>/dev/null || true) &

exec python -m uvicorn app.main:app --host "$HOST" --port "$PORT" --log-level info
