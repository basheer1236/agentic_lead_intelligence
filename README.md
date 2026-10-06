# 🏢 Agentic Lead Intelligence Platform

An enterprise-grade, autonomous multi-agent lead intelligence pipeline that automatically discovers, extracts, enriches, scores, and synthesizes high-intent residential interior design and architecture leads into relationally linked Excel workbooks and Cloud PostgreSQL.

---

## ⚡ Quick Start: How to Run in 3 Minutes

Follow these 4 simple steps to run the complete system on any computer (Windows, macOS, or Linux).

```
┌────────────────────────┐     ┌────────────────────────┐     ┌────────────────────────┐     ┌────────────────────────┐
│  1. Clone Repository   │ ──> │   2. 1-Click Setup     │ ──> │  3. Configure .env     │ ──> │    4. Launch App       │
│  git clone <repo_url>  │     │   setup.bat / setup.sh │     │  Add your API key      │     │  launch_ui.bat / .sh   │
└────────────────────────┘     └────────────────────────┘     └────────────────────────┘     └────────────────────────┘
```

---

### Step 1: Clone the Repository

Open your terminal (PowerShell, Command Prompt, or Terminal) and run:

```bash
git clone https://github.com/basheer1236/agentic_lead_intelligence.git
cd agentic_lead_intelligence
```

---

### Step 2: Run the One-Click Setup

This automatically creates your Python virtual environment (`.venv`), installs all required libraries, and downloads headless browser binaries.

* **On Windows (Easiest)**:
  Double-click `setup.bat` or run:
  ```cmd
  setup.bat
  ```

* **On macOS / Linux**:
  ```bash
  chmod +x setup.sh run.sh launch_ui.sh
  ./setup.sh
  ```

---

### Step 3: Configure Your API Key (`.env`)

Create a `.env` file in the project root folder (you can copy `.env.example`):

```env
# 1. Database Connection (Neon Cloud PostgreSQL)
DATABASE_URL=postgresql://<user>:<password>@<neon-endpoint>.neon.tech/neondb?sslmode=require

# 2. LLM Provider (Google Gemini is free and fast)
LLM_PROVIDER=gemini
LLM_API_KEY=your_gemini_api_key_here
LLM_MODEL=gemini-flash-latest

# 3. Web Search Provider (Optional - uses built-in mock if left empty)
SEARCH_PROVIDER=tavily
TAVILY_API_KEY=
```

> **Where to get a free Gemini API key?**  
> Go to [Google AI Studio](https://aistudio.google.com/) and click **Get API key** (it's 100% free with generous rate limits).

---

### Step 4: Launch and Use the Application!

#### Option A: Executive Web Dashboard (Recommended)
* **Windows**: Double-click `launch_ui.bat`
* **macOS / Linux**: Run `./launch_ui.sh`
* **Or via Terminal**:
  ```bash
  python -m app.ui.server
  ```
👉 Open your browser to **`http://localhost:8000`**!
* Click the blue **"Run Pipeline"** button.
* Watch real-time streaming logs as agents analyze articles.
* Click **"Download Excel"** when finished to get your formatted lead report.

#### Option B: Direct CLI Execution (Terminal Only)
* **Windows**: Double-click `run.bat`
* **macOS / Linux**: Run `./run.sh`
* Output files will be generated in `./data/exports/lead_intelligence_master.xlsx`.

#### Option C: In VS Code
1. Open the project in VS Code: `code .`
2. Press `Ctrl + Shift + D` (Run & Debug menu).
3. Select **"🚀 Launch Executive Dashboard (Web UI)"** and press `F5`.

---

## 🌐 Cloud Hosting Guide (Zero Docker / Native Python)

You can easily host this application on any cloud platform in under 3 minutes:

### Deploying to Render / Railway / Heroku
1. Connect your GitHub repository (`https://github.com/basheer1236/agentic_lead_intelligence`).
2. Set the service type to **Web Service** with **Python 3.11+**.
3. **Build Command**:
   ```bash
   pip install -r requirements.txt && playwright install --with-deps chromium
   ```
4. **Start Command**:
   ```bash
   uvicorn app.ui.server:app --host 0.0.0.0 --port $PORT
   ```
   *(A pre-configured `Procfile` is included)*.
5. **Health Check URL**: `/health` (returns HTTP 200 OK).
6. **Environment Variables**: Add `DATABASE_URL`, `LLM_PROVIDER`, `LLM_API_KEY`, and `LLM_MODEL` in your cloud settings.

### Deploying to Ubuntu / Linux VPS (AWS EC2, DigitalOcean)
```bash
git clone https://github.com/basheer1236/agentic_lead_intelligence.git
cd agentic_lead_intelligence
./setup.sh
# Configure your .env file
nano .env
# Start the background service using PM2 or systemd
pm2 start "uvicorn app.ui.server:app --host 0.0.0.0 --port 8000" --name "lead-intel"
```

---

## 🔄 Universal LLM Configuration

You are not locked into any single AI provider. Simply switch the provider and model in `.env` (or on the fly from the Web Dashboard at `http://localhost:8000`):

| Provider | `LLM_PROVIDER` | `LLM_MODEL` | Where to get Key |
| :--- | :--- | :--- | :--- |
| **Google Gemini** *(Default)* | `gemini` | `gemini-flash-latest` | [aistudio.google.com](https://aistudio.google.com/) |
| **Groq** *(Ultra Fast)* | `groq` | `llama-3.3-70b-versatile` | [console.groq.com](https://console.groq.com/) |
| **OpenRouter** *(Any Model)* | `openrouter` | `openai/gpt-4o-mini` | [openrouter.ai](https://openrouter.ai/) |
| **OpenAI** | `openai` | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com/) |
| **Local Ollama** *(Offline)* | `ollama` | `llama3:latest` | Runs locally via Ollama |

---

## 📊 Relational Excel Deliverables

Every pipeline run creates an institutional multi-tab workbook at `data/exports/lead_intelligence_master.xlsx` containing:

1. **`README`**: Methodologies, scoring algorithms, and column definitions.
2. **`Lead Intelligence Master`**: Project metadata, source articles, locations, estimated budgets, and carpet areas.
3. **`Interior Designer Master`**: Lead score (0–100), high-value flag, verified studio names, websites, Instagram URLs, and verified phone/email contact details.
4. **`Rug Opportunity Tracker`**: Dimension recommendations, luxury suitability scores, material/pattern requirements, and buyer intent.

---

## 🧪 Testing & Verification

To verify that all components, database pooling, LLM routing, and Excel export schemas are working properly:

```bash
pytest -v
```

---

## 🛠️ Project Structure

```text
agentic_lead_intelligence/
├── app/
│   ├── agents/          # LangGraph specialized agents (Relevance, Project, Rug, Designer)
│   ├── config/          # Pydantic environment settings
│   ├── export/          # 4-Sheet relational Excel exporter
│   ├── graph/           # Multi-agent state graph pipeline
│   ├── llm/             # Universal LLM client with backoff & token trimming
│   ├── models/          # Structured Pydantic domain models
│   ├── storage/         # SQLAlchemy database models & Neon connection engine
│   ├── tools/           # Web scrapers & Tavily public search tools
│   └── ui/              # FastAPI server, SSE live event streaming & Web Dashboard
├── data/
│   └── exports/         # Generated Excel workbooks
├── migrations/          # Alembic database migration versions
├── scripts/             # CLI pipeline execution scripts
├── tests/               # Automated unit and integration test suite
├── launch_ui.bat        # 1-Click Web Dashboard launcher (Windows)
├── launch_ui.sh         # 1-Click Web Dashboard launcher (macOS / Linux)
├── run.bat              # 1-Click CLI Pipeline launcher (Windows)
├── run.sh               # 1-Click CLI Pipeline launcher (macOS / Linux)
├── setup.bat            # 1-Click Dependency & DB installer (Windows)
├── setup.sh             # 1-Click Dependency & DB installer (macOS / Linux)
├── Procfile             # PaaS cloud deployment configuration
├── requirements.txt     # Python package dependencies
└── README.md            # Comprehensive project documentation
```