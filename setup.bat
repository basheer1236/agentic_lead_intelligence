@echo off
SETLOCAL EnableDelayedExpansion

echo ============================================================
echo AGENTIC LEAD INTELLIGENCE - ONE-CLICK SYSTEM SETUP
echo ============================================================

:: 1. Check Python installation
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is not installed or not added to system PATH.
    echo Please install Python 3.11+ from https://www.python.org/
    pause
    exit /b 1
)

echo [+] Python installation verified.

:: 2. Create Virtual Environment
IF NOT EXIST "venv" (
    echo [+] Creating Python virtual environment (venv)...
    python -m venv venv
) ELSE (
    echo [+] Virtual environment (venv) already exists.
)

:: 3. Activate Virtual Environment
call venv\Scripts\activate.bat

:: 4. Upgrade Pip and Install Dependencies
echo [+] Upgrading pip and installing dependencies from requirements.txt...
python -m pip install --upgrade pip
pip install -r requirements.txt

:: 5. Install Playwright Chromium Browser
echo [+] Installing Playwright Chromium browser binaries...
playwright install chromium

:: 6. Initialize Environment File (.env)
IF NOT EXIST ".env" (
    echo [+] Setting up environment variables...
    python scripts\init_env.py
) ELSE (
    echo [+] Configured .env file found.
)

:: 7. Run Database Migrations (Alembic)
echo [+] Running database migrations (Alembic)...
alembic upgrade head

echo ============================================================
echo SETUP COMPLETE! You can now run the pipeline by double-clicking 'run.bat'.
echo ============================================================
pause
