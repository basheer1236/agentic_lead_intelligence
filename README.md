# Agentic Lead Intelligence - Portable Deployment & Quick Start Guide

An enterprise-grade, autonomous multi-agent intelligence pipeline designed to extract, enrich, score, and synthesize high-intent residential interior design and architecture leads into relationally linked Excel workbooks and Cloud PostgreSQL (Neon).

---

##  Key Highlights & Architecture

* **Multi-Agent Pipeline**: Powered by LangGraph agents (Relevance Classifier, Project Metadata Extractor, Interior Designer Profiler, Public Search Verifier, Rug Opportunity Evaluator).
* **Universal LLM Client**: Built-in support for any LLM provider (Google Gemini, OpenRouter, OpenAI, Groq, Anthropic, DeepSeek, Ollama) via unified OpenAI-compatible endpoints with automated token trimming and exponential backoff retry.
* **Executive Web Dashboard**: Real-time FastAPI server with Server-Sent Events (SSE) streaming live terminal logs, manual execution trigger, batch size selector, test mode toggle, stop/abort control, database health monitor, and instant Excel export download.
* **Resilient Cloud Database**: Neon Serverless PostgreSQL integration with persistent connection pooling (`pool_pre_ping=True`, `pool_recycle=300`) and graceful SQLite offline fallback.
* **Relationally Linked Excel Workbooks**: Auto-generates multi-sheet Excel workbooks (`README`, `Lead Intelligence Master`, `Interior Designer Master`, `Rug Opportunity Tracker`) formatted according to commercial executive specifications.

---

## Prerequisites

1. **Python 3.11+**: Installed and available in PATH ([python.org](https://www.python.org/)).
2. **PostgreSQL Database** *(Recommended)*: A free serverless database on [Neon.tech](https://neon.tech/) or local PostgreSQL instance. *(Pipeline falls back to local SQLite if not configured)*.
3. **LLM API Key**: Google Gemini (Recommended / Free tier), OpenRouter, Groq, or OpenAI API key.
4. **Tavily AI Search Key** *(Optional)*: For verifying public designer portfolio websites and social URLs.

---

##  Quick Start

### Option A: Windows (1-Click Launchers)

1. **Initial Setup**:
   Double-click `setup.bat` (or run in PowerShell/CMD):
   ```cmd
   setup.bat
   ```
   *This automatically creates/activates the virtual environment (`.venv`), installs all dependencies, downloads Playwright browser binaries, guides you through `.env` creation, and executes Alembic database migrations.*

2. **Launch the Executive Web Dashboard** *(Recommended)*:
   Double-click `launch_ui.bat`:
   ```cmd
   launch_ui.bat
   ```
   *Automatically starts the FastAPI server and opens `http://localhost:8000` in your default browser.*

3. **Or Run CLI Pipeline Directly**:
   Double-click `run.bat`:
   ```cmd
   run.bat
   ```
   *Runs the pipeline in batch mode, records results to Neon PostgreSQL, and opens the `data/exports` directory containing the Excel sheets.*

---

### Option B: macOS / Linux

1. **Initial Setup**:
   ```bash
   chmod +x setup.sh run.sh
   ./setup.sh
   ```

2. **Launch the Executive Web Dashboard**:
   ```bash
   source .venv/bin/activate
   uvicorn app.ui.server:app --host 127.0.0.1 --port 8000 --reload
   ```
   Open `http://127.0.0.1:8000` in your web browser.

3. **Or Run CLI Pipeline Directly**:
   ```bash
   ./run.sh
   ```

---

### Option C: VS Code (IDE Experience)

The workspace includes pre-configured launch tasks (`.vscode/launch.json`):
1. Open the repository in VS Code: `code .`
2. Select Python Interpreter: Press `Ctrl+Shift+P` -> **Python: Select Interpreter** -> choose `./.venv/Scripts/python.exe`.
3. Open the **Run & Debug** panel (`Ctrl+Shift+D`):
   - Choose **"Executive Web UI (FastAPI)"** and press `F5` to start the dashboard.
   - Choose **"Run Pipeline CLI"** to debug article processing step-by-step.
   - Choose **"Run Pytest Suite"** to verify the test suite.

---

##  Configuration (`.env`)

Copy `.env.example` to `.env` if not already created:
```cmd
copy .env.example .env
```

### 1. Database Configuration (Neon PostgreSQL)
```env
# Neon Serverless PostgreSQL (Recommended):
DATABASE_URL=postgresql://<user>:<password>@ep-lucky-sound-b4drbw0w-pooler.c-6.us-east-2.aws.neon.tech/neondb?sslmode=require

# Local PostgreSQL Alternative:
# DATABASE_URL=postgresql://postgres:postgres@localhost:5432/lead_intelligence
```

### 2. Universal LLM Configuration

The pipeline supports any LLM provider by simply switching the provider name and model:

#### Google Gemini (Free / Fast - Default):
```env
LLM_PROVIDER=gemini
LLM_API_KEY=AIzaSy...
LLM_MODEL=gemini-flash-latest
# Optional: LLM_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/
```

#### OpenRouter:
```env
LLM_PROVIDER=openrouter
LLM_API_KEY=sk-or-v1-...
LLM_MODEL=openai/gpt-4o-mini
```

#### Groq:
```env
LLM_PROVIDER=groq
LLM_API_KEY=gsk_...
LLM_MODEL=llama-3.3-70b-versatile
```

#### OpenAI:
```env
LLM_PROVIDER=openai
LLM_API_KEY=sk-...
LLM_MODEL=gpt-4o-mini
```

#### Ollama (Local LLM):
```env
LLM_PROVIDER=ollama
LLM_API_KEY=ollama
LLM_MODEL=llama3:latest
LLM_BASE_URL=http://localhost:11434/v1
```

### 3. Public Web Search (Tavily AI)
```env
SEARCH_PROVIDER=tavily
TAVILY_API_KEY=tvly-...
# If left blank, the pipeline uses the built-in MockSearchProvider for graceful local execution.
```

---

## Output Artifacts & Deliverables

Every successful pipeline run generates structured relational deliverables:

1. **Relational Excel Workbooks (`data/exports/`)**:
   - `lead_intelligence_master.xlsx`: Full relational master workbook containing 4 synchronized tabs:
     * **`README`**: Executive summary, column definitions, scoring methodologies, and schema relationships.
     * **`Lead Intelligence Master`**: Project records, article source metadata, locations, estimated budgets, and carpet areas.
     * **`Interior Designer Master`**: Lead scoring (0–100), high-value flag, verified studio names, websites, Instagram URLs, city/country, and verified phone/email contact details.
     * **`Rug Opportunity Tracker`**: Sizing recommendations, bespoke luxury suitability scores, material/pattern requirements, and buyer intent assessment.
   - `lead_intelligence.xlsx`: Timestamped standard run export.

2. **Neon Cloud Database**:
   - Persisted across normalized tables (`projects`, `designers`, `rug_opportunities`, `pipeline_runs`) queryable via SQL or BI tools.

---

## Testing & Verification

Run the comprehensive pytest suite:
```cmd
pytest -v
```
Verifies:
* Universal LLM client provider routing and mock fallback.
* Neon PostgreSQL connection pooling, reconnect resilience, and schema binding.
* FastAPI Web UI health check, streaming endpoints, and runner state machine.
* Multi-sheet Excel workbook export integrity and column headers.
