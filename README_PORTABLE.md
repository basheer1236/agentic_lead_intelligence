# Agentic Lead Intelligence - Portable Deployment & Hosting Guide

An enterprise-grade, autonomous multi-agent lead intelligence pipeline designed to discover, enrich, score, and synthesize high-intent residential interior design and architecture leads into relationally linked Excel workbooks and Cloud PostgreSQL (Neon).

---

## 🚀 System Architecture & Capabilities

* **Autonomous Multi-Agent Pipeline**: LangGraph workflow coordinating specialized agents (Relevance Classifier, Project Metadata Extractor, Interior Designer Profiler, Public Web Search Verifier, Rug Opportunity Evaluator).
* **Universal LLM Engine**: Native provider routing for **Google Gemini**, **OpenRouter**, **Groq**, **OpenAI**, **DeepSeek**, and local **Ollama** via unified OpenAI-compatible endpoints with automated prompt trimming, exponential backoff retries, and inter-article rate pacing.
* **Executive Web Dashboard**: FastAPI server with Server-Sent Events (SSE) streaming live execution logs, interactive "Run Pipeline" trigger, batch size selector, test mode toggle, stop control, database health monitor, and one-click Excel download.
* **Resilient Cloud Database**: Neon Serverless PostgreSQL integration with persistent connection pooling (`pool_pre_ping=True`, `pool_recycle=300`), automatic table initialization on startup, and graceful offline fallback.
* **Executive Relational Excel Workbooks**: Generates 4 synchronized, relationally linked tabs (`README`, `Lead Intelligence Master`, `Interior Designer Master`, `Rug Opportunity Tracker`) formatted to institutional reporting standards.

---

## 📋 System Requirements & Prerequisites

1. **Python 3.11+**: Installed and accessible in PATH.
2. **Cloud PostgreSQL** *(Recommended)*: A free serverless database on [Neon.tech](https://neon.tech/) (or local PostgreSQL).
3. **LLM API Key**: Google Gemini (Recommended / Fast & Free tier), OpenRouter, Groq, or OpenAI.
4. **Tavily Search API Key** *(Optional)*: For verifying public designer portfolio websites and social URLs.

---

## 🌐 Cloud Hosting & Server Deployment Guide (Python Native / Zero Docker)

This application is built with standard Python and FastAPI, making it extremely lightweight and straightforward to host on any cloud platform or server without Docker.

### Method 1: Cloud PaaS (Render, Railway, Fly.io, Heroku)

Deploying to modern cloud platforms takes under 3 minutes:

1. **Push Repository**: Connect your GitHub repository (`https://github.com/basheer7526/agentic-lead-intelligence`) to your platform.
2. **Configure Service Settings**:
   * **Environment**: `Python 3.11+`
   * **Build Command**:
     ```bash
     pip install -r requirements.txt && playwright install --with-deps chromium
     ```
   * **Start Command**:
     ```bash
     uvicorn app.ui.server:app --host 0.0.0.0 --port $PORT
     ```
     *(A pre-configured `Procfile` is already included in the root directory)*.
   * **Health Check Path**: `/health` (returns `200 OK`)
3. **Set Environment Variables**:
   Add the following in your platform's **Environment Variables / Config Vars** dashboard:
   | Variable | Value | Description |
   | :--- | :--- | :--- |
   | `DATABASE_URL` | `postgresql://<user>:<pwd>@<endpoint>.neon.tech/neondb?sslmode=require` | Neon PostgreSQL cloud connection |
   | `LLM_PROVIDER` | `gemini` | Provider name (`gemini`, `openrouter`, `groq`, `openai`) |
   | `LLM_API_KEY` | `AIzaSy...` | Your LLM provider API key |
   | `LLM_MODEL` | `gemini-flash-latest` | Model identifier |
   | `TAVILY_API_KEY` | *(Optional)* | Tavily Search key (if left blank, uses mock search) |
   | `SEARCH_PROVIDER` | `tavily` | Search engine provider |

4. **Deploy**:
   The host will build dependencies, run migrations/table initialization automatically on startup, and serve the dashboard on your assigned URL!

---

### Method 2: Linux VPS / Ubuntu Server (AWS EC2, DigitalOcean, Linode)

To host on a standard Linux virtual server:

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/basheer7526/agentic-lead-intelligence.git
   cd agentic-lead-intelligence
   ```

2. **Run One-Click Setup**:
   ```bash
   chmod +x setup.sh run.sh launch_ui.sh
   ./setup.sh
   ```
   *This automatically creates `.venv`, installs dependencies, downloads Playwright Chromium, prompts for keys, and initializes the database.*

3. **Configure Environment File**:
   Ensure `.env` exists with your keys:
   ```bash
   nano .env
   ```

4. **Run as a Background Production Service**:
   You can run the web dashboard using **PM2**, **systemd**, or **tmux**:

   *Using PM2:*
   ```bash
   npm install -g pm2
   pm2 start "uvicorn app.ui.server:app --host 0.0.0.0 --port 8000" --name "lead-intel"
   pm2 save
   pm2 startup
   ```

   *Or Using systemd (`/etc/systemd/system/lead-intel.service`):*
   ```ini
   [Unit]
   Description=Agentic Lead Intelligence Web Dashboard
   After=network.target

   [Service]
   User=ubuntu
   WorkingDirectory=/home/ubuntu/agentic-lead-intelligence
   ExecStart=/home/ubuntu/agentic-lead-intelligence/.venv/bin/uvicorn app.ui.server:app --host 0.0.0.0 --port 8000
   Restart=always
   EnvironmentFile=/home/ubuntu/agentic-lead-intelligence/.env

   [Install]
   WantedBy=multi-user.target
   ```
   Enable and start the service:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable lead-intel
   sudo systemctl start lead-intel
   ```

5. Access the live dashboard at `http://<your-server-ip>:8000`.

---

## 💻 Local Workstation Setup & Execution

### Windows (1-Click Launchers)

1. **First-Time Setup**:
   Double-click `setup.bat` (or execute in PowerShell):
   ```cmd
   setup.bat
   ```
   *(Creates `.venv`, installs dependencies, downloads browser binaries, guides `.env` setup, and initializes DB).*

2. **Launch the Executive Web Dashboard**:
   Double-click `launch_ui.bat`:
   ```cmd
   launch_ui.bat
   ```
   *Automatically starts the FastAPI server and opens `http://localhost:8000` in your default browser.*

3. **Or Run Pipeline Directly via CLI**:
   Double-click `run.bat`:
   ```cmd
   run.bat
   ```
   *Processes RSS articles, writes leads to Neon DB, and opens `data/exports/` with generated Excel files.*

---

### macOS / Linux

1. **First-Time Setup**:
   ```bash
   chmod +x setup.sh run.sh launch_ui.sh
   ./setup.sh
   ```

2. **Launch Web Dashboard**:
   ```bash
   ./launch_ui.sh
   ```
   Open `http://localhost:8000` in your browser.

3. **Or Run CLI Pipeline**:
   ```bash
   ./run.sh
   ```

---

### VS Code (IDE Experience)

Pre-configured launch profiles are provided in `.vscode/launch.json`:
1. Open the project in VS Code: `code .`
2. Select Python Interpreter: `Ctrl+Shift+P` -> **Python: Select Interpreter** -> `./.venv/Scripts/python.exe`.
3. Open **Run & Debug** (`Ctrl+Shift+D`):
   - **Executive Web UI (FastAPI)**: Press `F5` to start the live dashboard.
   - **Run Pipeline CLI**: Step through the pipeline in debug mode.
   - **Run Pytest Suite**: Execute unit and architecture validation tests.

---

## ⚙️ Universal LLM Configuration Recipes (`.env`)

You can switch LLM providers at any time by updating `.env` (or via the **Live Configuration** card on the Web Dashboard):

### 1. Google Gemini (Recommended - Fast & High Rate Limits)
```env
LLM_PROVIDER=gemini
LLM_API_KEY=AIzaSy...
LLM_MODEL=gemini-flash-latest
```

### 2. OpenRouter (Access to Claude, GPT-4o, DeepSeek, etc.)
```env
LLM_PROVIDER=openrouter
LLM_API_KEY=sk-or-v1-...
LLM_MODEL=openai/gpt-4o-mini
```

### 3. Groq (Ultra-Fast Inference)
```env
LLM_PROVIDER=groq
LLM_API_KEY=gsk_...
LLM_MODEL=llama-3.3-70b-versatile
```

### 4. OpenAI
```env
LLM_PROVIDER=openai
LLM_API_KEY=sk-proj-...
LLM_MODEL=gpt-4o-mini
```

### 5. Local Ollama (Zero Cost / Offline)
```env
LLM_PROVIDER=ollama
LLM_API_KEY=ollama
LLM_MODEL=llama3:latest
LLM_BASE_URL=http://localhost:11434/v1
```

---

## 📊 Deliverables & Export Structure

Every pipeline run produces synchronized deliverables:

1. **Excel Workbooks (`data/exports/`)**:
   - `lead_intelligence_master.xlsx`: Full relational master workbook containing 4 synchronized worksheets:
     * **`README`**: Methodologies, scoring logic, field definitions, and schema relationships.
     * **`Lead Intelligence Master`**: Project metadata, source articles, locations, estimated budgets, and carpet areas.
     * **`Interior Designer Master`**: Lead scores (0–100), high-value qualification flag, studio names, website URLs, Instagram links, and verified contact numbers.
     * **`Rug Opportunity Tracker`**: Dimension recommendations, luxury suitability scores, material/pattern requirements, and buyer intent.
   - `lead_intelligence.xlsx`: Timestamped export.

2. **Neon Cloud PostgreSQL**:
   - Persisted across normalized tables (`projects`, `designers`, `rug_opportunities`, `scores`, `pipeline_runs`) queryable by external BI tools or SQL clients.

---

## 🧪 Automated Testing

Execute the automated test suite to verify end-to-end system health:
```bash
pytest -v
```
Validates:
* Universal LLM client routing, token trimming, and backoff retries.
* Neon PostgreSQL connection pooling, reconnect resilience, and schema binding.
* FastAPI dashboard routes, SSE event streaming, and `/health` monitor.
* Multi-sheet Excel workbook export integrity and column schemas.
