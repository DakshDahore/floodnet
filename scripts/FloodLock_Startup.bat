@echo off
REM Project FloodLock - Autonomous Background Startup on Windows Boot
title FloodLock Auto Sentinel

echo [FloodLock] Starting Windows local compute node services...

REM 1. Start FastAPI Backend on Port 8000
cd /d "C:\Users\YuvaMPS1\Documents\server\floodlock\floodlock_backend_local"
start "FloodLock_FastAPI" /b python -m uvicorn app:app --host 0.0.0.0 --port 8000

REM 2. Start Cloudflare Tunnel
cd /d "C:\Users\YuvaMPS1\Documents\server\floodlock"
if exist "cloudflared.exe" (
  start "FloodLock_Tunnel" /b cloudflared.exe tunnel --url http://127.0.0.1:8000 --logfile "tunnel.log"
)

echo [FloodLock] Services started successfully.
