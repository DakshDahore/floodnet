#!/usr/bin/env bash
set -e
echo "=================================================================="
echo " PROJECT FLOODLOCK // FASTAPI ANALYTICAL BACKEND MICROSERVICE"
echo "=================================================================="
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [ -f "../.venv/bin/uvicorn" ]; then
    UVICORN_BIN="../.venv/bin/uvicorn"
elif command -v uvicorn &> /dev/null; then
    UVICORN_BIN="uvicorn"
else
    UVICORN_BIN="python3 -m uvicorn"
fi

echo "[*] Launching Uvicorn server on http://0.0.0.0:8000"
$UVICORN_BIN app:app --host 0.0.0.0 --port 8000 --reload
