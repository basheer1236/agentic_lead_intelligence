# Agentic Lead Intelligence - Quick Start Guide for New Systems

This guide explains how to set up and run the **Agentic Lead Intelligence Pipeline** on any laptop or workstation (Windows, macOS, or Linux).

---

## Prerequisites
1. **Python 3.11+**: Download and install from [python.org](https://www.python.org/).
2. **Database Access**: A PostgreSQL database connection URL (either local or cloud hosted).
3. **API Keys**:
   * **LLM API Key** (OpenAI / Gemini / Groq)
   * **Tavily Search API Key** (for public designer verification)

---

## Quick Start (2-Step Setup)

### On Windows:

1. **First-Time Setup**:
   Double-click `setup.bat` (or run in CMD / PowerShell):
   ```cmd
   setup.bat
   ```
   *This creates the virtual environment, installs dependencies, downloads headless Playwright Chromium, prompts for your API keys, and runs database migrations.*

2. **Run Pipeline**:
   Double-click `run.bat`:
   ```cmd
   run.bat
   ```
   *This executes the pipeline, updates PostgreSQL, and automatically opens the `data/exports` folder with the updated Excel lead reports!*

---

### On macOS / Linux:

1. **First-Time Setup**:
   Open Terminal in the project directory and run:
   ```bash
   chmod +x setup.sh run.sh
   ./setup.sh
   ```

2. **Run Pipeline**:
   ```bash
   ./run.sh
   ```

---

## Output Artifacts

The pipeline generates relationally linked Excel reports in `data/exports/`:
* `lead_intelligence_master.xlsx`: Full master report containing 4 worksheets (`README`, `Lead Intelligence Master`, `Interior Designer Master`, and `Rug Opportunity Tracker`).
* `lead_intelligence.xlsx`: Standard export.

---

## Re-configuring API Keys or Database URL

If you need to update your API keys or PostgreSQL connection URL at any time, edit the `.env` file in the root directory or run:
```bash
python scripts/init_env.py
```
