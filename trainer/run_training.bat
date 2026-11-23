@echo off
title FloodLock Neural Trainer Suite
echo ==================================================================
echo  PROJECT FLOODLOCK // NEURAL TRAINER PIPELINE
echo ==================================================================
cd /d "%~dp0"

if exist "..\.venv\Scripts\python.exe" (
    set "PYTHON_BIN=..\.venv\Scripts\python.exe"
) else if exist ".venv\Scripts\python.exe" (
    set "PYTHON_BIN=.venv\Scripts\python.exe"
) else (
    set "PYTHON_BIN=python"
)

REM 1. Synthesize Physics Data
%PYTHON_BIN% generate_datasets.py
if %ERRORLEVEL% neq 0 (
    echo [!] Dataset generation failed!
    pause
    exit /b %ERRORLEVEL%
)

REM 2. Audit Model Parameter Counts
%PYTHON_BIN% models.py
if %ERRORLEVEL% neq 0 (
    echo [!] Model parameter count audit failed!
    pause
    exit /b %ERRORLEVEL%
)

REM 3. Train Dual Neural Networks and Export Real Weights
%PYTHON_BIN% train_models.py
if %ERRORLEVEL% neq 0 (
    echo [!] Model training failed!
    pause
    exit /b %ERRORLEVEL%
)

echo ==================================================================
echo  [✓] ALL TRAINER PIPELINES COMPLETED SUCCESSFULLY
echo ==================================================================
pause
