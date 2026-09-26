#!/bin/bash
set -e

echo "============================================================"
echo "RUNNING AGENTIC LEAD INTELLIGENCE PIPELINE (UNIX)"
echo "============================================================"

if [ ! -d "venv" ]; then
    echo "[ERROR] Virtual environment not found. Please run './setup.sh' first."
    exit 1
fi

source venv/bin/activate

python scripts/run_pipeline.py

echo ""
echo "============================================================"
echo "PIPELINE COMPLETE! Excel exports generated in ./data/exports/"
echo "============================================================"
