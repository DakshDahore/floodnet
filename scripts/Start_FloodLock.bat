@echo off
REM Project FloodLock - Desktop Launcher
title FloodLock Sentinel Services
echo [FloodLock] Checking and starting background compute services...

REM 1. Ensure Ollama service is active
netstat -ano | findstr ":11434" | findstr "LISTENING" >nul
if %errorlevel% neq 0 (
  echo [FloodLock] Starting Ollama SLM server...
  start "Ollama_Service" /min "%LOCALAPPDATA%\Programs\Ollama\ollama.exe" serve
  timeout /t 3 >nul
) else (
  echo [FloodLock] Ollama is active on port 11434.
)

REM 2. Ensure FastAPI Backend is active
netstat -ano | findstr ":8000" | findstr "LISTENING" >nul
if %errorlevel% neq 0 (
  echo [FloodLock] Starting FastAPI Hydrodynamic Backend...
  cd /d "C:\Users\YuvaMPS1\Documents\server\floodlock\floodlock_backend_local"
  start "FloodLock_FastAPI" /min python -m uvicorn app:app --host 0.0.0.0 --port 8000
  timeout /t 2 >nul
) else (
  echo [FloodLock] FastAPI Backend is active on port 8000.
)

REM 3. Ensure Cloudflare Tunnel is active
tasklist /fi "imagename eq cloudflared.exe" | findstr /i "cloudflared.exe" >nul
if %errorlevel% neq 0 (
  echo [FloodLock] Starting Cloudflare Tunnel...
  cd /d "C:\Users\YuvaMPS1\Documents\server\floodlock"
  if exist "cloudflared.exe" (
    start "FloodLock_Tunnel" /min cloudflared.exe tunnel --url http://127.0.0.1:8000 --logfile "C:\Users\YuvaMPS1\Documents\server\floodlock\tunnel.log"
  )
) else (
  echo [FloodLock] Cloudflare Tunnel is running.
)

echo.
echo =======================================================
echo [OK] FloodLock services are LIVE!
echo Telemetry endpoint: http://127.0.0.1:8000/health
echo =======================================================
timeout /t 4 >nul
