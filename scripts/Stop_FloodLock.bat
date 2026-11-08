@echo off
REM Project FloodLock - Desktop Stop Script
title Stop FloodLock Services
echo [FloodLock] Terminating background compute services...

taskkill /f /im cloudflared.exe >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8000" ^| findstr "LISTENING"') do (
  taskkill /f /pid %%a >nul 2>&1
)

echo.
echo =======================================================
echo [OK] FloodLock FastAPI and Tunnel have been stopped.
echo =======================================================
timeout /t 3 >nul
