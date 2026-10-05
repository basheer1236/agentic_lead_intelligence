@echo off
SETLOCAL EnableDelayedExpansion

echo ============================================================
echo   AGENTIC LEAD INTELLIGENCE - EXECUTIVE DASHBOARD
echo ============================================================

IF EXIST ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
) ELSE IF EXIST "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) ELSE (
    echo [ERROR] Python virtual environment not found (.venv or venv).
    pause
    exit /b 1
)

set PYTHONPATH=.

echo.
echo [+] Launching dashboard server on http://localhost:8000...
echo [+] Opening your browser...
echo.

start "" "http://localhost:8000"

python -m app.ui.server

pause
