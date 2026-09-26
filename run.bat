@echo off
SETLOCAL EnableDelayedExpansion

echo ============================================================
echo RUNNING AGENTIC LEAD INTELLIGENCE PIPELINE
echo ============================================================

IF NOT EXIST "venv" (
    echo [ERROR] Virtual environment not found. Please run 'setup.bat' first.
    pause
    exit /b 1
)

call venv\Scripts\activate.bat

python scripts\run_pipeline.py

echo.
echo ============================================================
echo PIPELINE COMPLETE! Opening Excel exports directory...
echo ============================================================
start data\exports

pause
