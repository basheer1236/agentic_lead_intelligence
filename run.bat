@echo off
setlocal

echo ============================================================
echo RUNNING AGENTIC LEAD INTELLIGENCE PIPELINE
echo ============================================================

set "PY_EXE="
if exist ".venv\Scripts\python.exe" set "PY_EXE=.venv\Scripts\python.exe"
if not defined PY_EXE if exist "venv\Scripts\python.exe" set "PY_EXE=venv\Scripts\python.exe"

if not defined PY_EXE (
    echo [ERROR] Python virtual environment not found. Please run setup.bat first.
    pause
    exit /b 1
)

set "PYTHONPATH=."
"%PY_EXE%" scripts\run_pipeline.py

echo.
echo ============================================================
echo PIPELINE COMPLETE! Opening Excel exports directory...
echo ============================================================
if exist "data\exports" (
    start data\exports
)

pause
