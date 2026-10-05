#!/bin/bash
set -e

echo "============================================================"
echo "  AGENTIC LEAD INTELLIGENCE - EXECUTIVE DASHBOARD (UNIX)"
echo "============================================================"

if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
elif [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
else
    echo "[ERROR] Python virtual environment not found (.venv or venv)."
    echo "Please run './setup.sh' first."
    exit 1
fi

export PYTHONPATH=.

PORT=${PORT:-8000}
HOST=${HOST:-0.0.0.0}

echo ""
echo "[+] Starting dashboard server on http://${HOST}:${PORT}..."
echo "[+] Visit http://localhost:${PORT} in your browser."
echo ""

uvicorn app.ui.server:app --host "$HOST" --port "$PORT"
