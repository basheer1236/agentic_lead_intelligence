@echo off
setlocal

echo ============================================================
echo AGENTIC LEAD INTELLIGENCE - ONE-CLICK SYSTEM SETUP
echo ============================================================

:: 1. Check Python installation
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python is not installed or not added to system PATH.
    echo Please install Python 3.11+ from https://www.python.org/
    echo Make sure to check 'Add python.exe to PATH' during install.
    pause
    exit /b 1
)

echo [+] Python installation verified.

:: 2. Create Virtual Environment (.venv)
if not exist ".venv\Scripts\python.exe" (
    echo [+] Creating Python virtual environment in .venv...
    python -m venv .venv
) else (
    echo [+] Virtual environment .venv already exists.
)

set "PY_EXE=.venv\Scripts\python.exe"

:: 3. Upgrade Pip and Install Dependencies
echo [+] Installing dependencies from requirements.txt...
"%PY_EXE%" -m pip install --upgrade pip
"%PY_EXE%" -m pip install -r requirements.txt

:: 4. Install Playwright Chromium Browser
echo [+] Installing Playwright Chromium browser binaries...
"%PY_EXE%" -m playwright install chromium

:: 5. Copy .env.example to .env if .env does not exist
if not exist ".env" (
    if exist ".env.example" (
        echo [+] Creating default .env from .env.example...
        copy .env.example .env >nul
        echo [+] Created .env configuration file.
    )
)

echo.
echo ============================================================
echo SETUP COMPLETE!
echo You can now start the web dashboard by double-clicking 'launch_ui.bat'
echo ============================================================
pause
