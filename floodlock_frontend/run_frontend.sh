#!/usr/bin/env bash
# floodlock_frontend/run_frontend.sh
# Serves the 4K Ultra-HD Frontend locally on port 3000
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
cd "$DIR"
echo "[FloodLock] Starting local frontend server on http://localhost:3000"
python3 -m http.server 3000
