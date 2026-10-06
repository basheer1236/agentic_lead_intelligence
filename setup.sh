#!/bin/bash
set -e

echo "============================================================"
echo "AGENTIC LEAD INTELLIGENCE - ONE-CLICK SYSTEM SETUP (UNIX)"
echo "============================================================"

# 1. Check Python installation
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python3 is not installed."
    echo "Please install Python 3.11+ using your package manager or python.org."
    exit 1
fi

echo "[+] Python3 installation verified."

# 2. Create Virtual Environment (.venv)
if [ ! -f ".venv/bin/python" ]; then
    echo "[+] Creating Python virtual environment in .venv..."
    python3 -m venv .venv
else
    echo "[+] Virtual environment (.venv) already exists."
fi

# 3. Upgrade Pip and Install Dependencies
echo "[+] Upgrading pip and installing dependencies..."
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt

# 4. Install Playwright Chromium Browser
echo "[+] Installing Playwright Chromium browser binaries..."
.venv/bin/python -m playwright install chromium

# 5. Copy .env.example to .env if .env does not exist
if [ ! -f ".env" ] && [ -f ".env.example" ]; then
    echo "[+] Creating default .env from .env.example..."
    cp .env.example .env
fi

echo ""
echo "============================================================"
echo "SETUP COMPLETE! You can now start the dashboard by running './launch_ui.sh'"
echo "============================================================"
