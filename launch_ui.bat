@echo off
setlocal

echo ============================================================
echo   AGENTIC LEAD INTELLIGENCE - EXECUTIVE DASHBOARD
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

echo.
echo [+] Freeing port 8000 if occupied...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8000" ^| findstr "LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1
)

echo [+] Launching dashboard server on http://localhost:8000...
echo [+] Opening your browser...
echo.

start "" "http://localhost:8000"

"%PY_EXE%" -m app.ui.server

pause
