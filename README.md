# 🏢 Agentic Lead Intelligence Platform

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Render-46E3B7?style=for-the-badge&logo=render&logoColor=white)](https://agentic-lead-intelligence-mgys.onrender.com)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Neon.tech-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://neon.tech/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Multi--Agent-FF6F00?style=for-the-badge)](https://langchain-ai.github.io/langgraph/)

An autonomous multi-agent intelligence pipeline designed to extract, enrich, score, and synthesize high-intent residential interior design and architecture leads from Architectural Digest India into relationally linked Excel workbooks and Cloud PostgreSQL (Neon).

---

## 🌐 Live Web Demo

Access the hosted executive dashboard directly in your browser:
👉 **[https://agentic-lead-intelligence-mgys.onrender.com](https://agentic-lead-intelligence-mgys.onrender.com)**

---

## 🚀 Local Quickstart (Run on Any Laptop)

### Step 1: Clone the Repository
```bash
git clone https://github.com/basheer1236/agentic_lead_intelligence.git
cd agentic_lead_intelligence
```

### Step 2: One-Click Environment Setup

#### **Windows**:
Double-click `setup.bat` or run in PowerShell / Command Prompt:
```powershell
.\setup.bat
```
*(Creates `.venv`, installs all packages, installs Playwright browsers, and prepares `.env`)*

#### **macOS / Linux**:
```bash
chmod +x setup.sh launch_ui.sh run.sh
./setup.sh
```

---

### Step 3: Launch the Executive Dashboard

#### **Windows**:
Double-click `launch_ui.bat` or run:
```powershell
.\launch_ui.bat
```

#### **macOS / Linux**:
```bash
./launch_ui.sh
```

#### **VS Code Terminal**:
```powershell
.\.venv\Scripts\python.exe -m app.ui.server
```

Open your browser at:
👉 **`http://localhost:8000`**

---

### Step 4: Configure Settings & Start

1. Click **Settings (⚙️)** in the top right corner of the dashboard.
2. Select your AI provider (**Google Gemini**, **Groq**, **OpenRouter**, **OpenAI**, **Anthropic**, or local **Ollama**).
3. Paste your **AI Access Key** (and optional **Tavily Key**).
4. Click **Save all settings**.
5. Select the number of articles to check (e.g. 5) and click **Start search**.

---

## 🔑 Universal LLM & Configuration

You can configure your settings via the **Settings (⚙️)** modal in the dashboard or directly in `.env`:

| Provider | Recommended Model | API Key Format |
| :--- | :--- | :--- |
| **Google Gemini** *(Free & Fast)* | `gemini-flash-latest` or `gemini-2.0-flash` | `AIzaSy...` |
| **Groq** *(Ultra Fast)* | `llama-3.3-70b-versatile` | `gsk_...` |
| **OpenRouter** *(Universal)* | `openai/gpt-4o-mini` or `deepseek/deepseek-chat` | `sk-or-v1-...` |
| **OpenAI** | `gpt-4o-mini` | `sk-proj-...` |
| **Anthropic** | `claude-3-5-sonnet-20241022` | `sk-ant-...` |
| **Ollama (Local Offline)** | `llama3:latest` | `ollama` *(Zero cost)* |

### Web Search (Tavily AI)
* **Live Search**: Provide your `TAVILY_API_KEY` (`tvly-...`) for real-time portfolio verification.
* **Mock Search**: If left blank, the pipeline automatically falls back to offline Mock Search without crashing or requiring any key.

### Database (Neon PostgreSQL)
* Connects seamlessly to serverless PostgreSQL (e.g. Neon.tech).
* Automatically falls back to local SQLite if no external database is configured.

---

## 🛡️ Pre-Flight Verification & Governance

* **Stage 0 Pre-Flight Checks**: Validates database connectivity and LLM credentials before initiating network operations. If an LLM API key is missing, execution halts immediately at **0%** with a clear explanation in the activity log.
* **Instant Abort & Restart**: The operator can stop execution at any time; the pipeline transitions to `Stopped` instantly and re-enables the search trigger.
* **Deterministic RSS & Dedup**: Stages 1–3 filter articles deterministically without consuming LLM tokens.
* **LangGraph Multi-Agent Analysis**: Stage 4 routes residential articles through specialized agents for designer attribution, contact extraction, and bespoke rug opportunity scoring.

---

## 📊 Deliverables & Output Files

Every pipeline execution generates commercial-grade deliverables:

1. **Relational Excel Workbooks (`data/exports/`)**:
   - `lead_intelligence_master.xlsx`: Full relational master workbook containing 4 synchronized sheets:
     - **`README`**: Methodology, score weighting (0–100), and schema documentation.
     - **`Lead Intelligence Master`**: Project metadata, article URLs, carpet areas, and locations.
     - **`Interior Designer Master`**: Designer names, studios, verified website/social links, phone/email, and qualification scores.
     - **`Rug Opportunity Tracker`**: Room dimensions, placement recommendations, custom sizing, and material requirements.
2. **Neon Cloud Database**:
   - Persisted across relational tables (`projects`, `designers`, `rug_opportunities`, `pipeline_runs`) queryable via SQL and BI tools.
3. **One-Click Download**:
   - Direct download links in the dashboard for instant access to exported `.xlsx` files.

---

## 🧪 Testing

Run the full automated test suite:
```bash
pytest -v
```
Verifies:
* Universal LLM client routing, token safety, and error handling.
* Neon PostgreSQL connection pooling and reconnect resilience.
* FastAPI Web UI streaming SSE endpoints, health status, and state machine.
* Multi-sheet Excel export integrity.
