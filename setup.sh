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

# 2. Create / Activate Virtual Environment
if [ -d ".venv" ]; then
    echo "[+] Existing virtual environment (.venv) detected."
    source .venv/bin/activate
elif [ -d "venv" ]; then
    echo "[+] Existing virtual environment (venv) detected."
    source venv/bin/activate
else
    echo "[+] Creating Python virtual environment (.venv)..."
    python3 -m venv .venv
    source .venv/bin/activate
fi

# 4. Upgrade Pip and Install Dependencies
echo "[+] Upgrading pip and installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# 5. Install Playwright Chromium Browser
echo "[+] Installing Playwright Chromium browser binaries..."
playwright install chromium

# 6. Initialize Environment File (.env)
if [ ! -f ".env" ]; then
    echo "[+] Setting up environment variables..."
    python scripts/init_env.py
else
    echo "[+] Configured .env file found."
fi

# 7. Run Database Migrations (Alembic)
echo "[+] Running database migrations (Alembic)..."
alembic upgrade head

echo "============================================================"
echo "SETUP COMPLETE! You can now run the pipeline by running './run.sh'."
echo "============================================================"
