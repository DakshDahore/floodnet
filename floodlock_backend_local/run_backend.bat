@echo off
title FloodLock Backend Server
echo ==================================================================
echo  PROJECT FLOODLOCK // FASTAPI ANALYTICAL BACKEND MICROSERVICE
echo ==================================================================
cd /d "%~dp0"

echo [*] Launching FastAPI Uvicorn server on http://0.0.0.0:8000
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
pause
