#!/bin/bash
set -e

echo "============================================================"
echo "RUNNING AGENTIC LEAD INTELLIGENCE PIPELINE (UNIX)"
echo "============================================================"

if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
elif [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
else
    echo "[ERROR] Virtual environment not found (.venv or venv). Please run './setup.sh' first."
    exit 1
fi

python scripts/run_pipeline.py

echo ""
echo "============================================================"
echo "PIPELINE COMPLETE! Excel exports generated in ./data/exports/"
echo "============================================================"
