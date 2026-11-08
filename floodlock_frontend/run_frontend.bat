@echo off
REM floodlock_frontend/run_frontend.bat
REM Serves the 4K Ultra-HD Frontend locally on port 3000
cd /d "%~dp0"
echo [FloodLock] Starting local frontend server on http://localhost:3000
python -m http.server 3000
pause
