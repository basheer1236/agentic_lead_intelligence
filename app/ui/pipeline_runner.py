import os
import sys
import time
import queue
import logging
import threading
from datetime import datetime
from typing import Dict, Any, List, Optional

from app.tools.rss_tool import fetch_rss_feed
from app.tools.article_filter import filter_articles
from app.tools.dedup import deduplicate_articles
from app.tools.http_tool import fetch_article
from app.tools.article_parser import parse_article
from app.graph.graph import graph
from app.config.settings import settings
from app.storage.database import SessionLocal, init_db
from app.export.excel_exporter import ExcelExporter
from app.errors import InvalidConfigurationError

logger = logging.getLogger(__name__)

# Standardized Pipeline Lifecycle States
STATUS_IDLE = "IDLE"
STATUS_RUNNING = "RUNNING"
STATUS_COMPLETED = "COMPLETED"
STATUS_FAILED = "FAILED"
STATUS_ABORTED = "ABORTED"


class PipelineRunner:
    """
    Observable, thread-safe pipeline coordinator.
    Explicitly triggered only on user demand.
    Lifecycle states strictly adhere to: IDLE, RUNNING, COMPLETED, FAILED, ABORTED.
    """

    def __init__(self):
        self._lock = threading.Lock()
        self._thread: Optional[threading.Thread] = None
        self._cancel_requested = False
        self._run_id = 0
        self._subscribers: List[queue.Queue] = []

        # Current state snapshot
        self.state: Dict[str, Any] = {
            "status": STATUS_IDLE,
            "current_stage": 0,
            "stage_name": "Ready",
            "progress_percent": 0,
            "current_article": None,
            "total_articles": 0,
            "start_time": None,
            "elapsed_seconds": 0,
            "metrics": {
                "evaluated": 0,
                "persisted": 0,
                "irrelevant": 0,
                "skipped": 0,
                "failed": 0,
                "rugs_found": 0,
            },
            "latest_export_files": [],
        }
        self.logs: List[Dict[str, Any]] = []

    def subscribe(self) -> queue.Queue:
        q = queue.Queue(maxsize=100)
        with self._lock:
            self._subscribers.append(q)
        return q

    def unsubscribe(self, q: queue.Queue):
        with self._lock:
            if q in self._subscribers:
                self._subscribers.remove(q)

    def _broadcast(self, event_type: str, data: Any):
        payload = {"type": event_type, "data": data, "timestamp": datetime.now().isoformat()}
        with self._lock:
            for q in list(self._subscribers):
                try:
                    q.put_nowait(payload)
                except queue.Full:
                    pass

    def add_log(self, level: str, message: str, run_id: Optional[int] = None):
        with self._lock:
            if run_id is not None and run_id != self._run_id:
                return
            now_str = datetime.now().strftime("%H:%M:%S")
            log_entry = {
                "timestamp": now_str,
                "level": level.upper(),
                "message": message,
            }
            self.logs.append(log_entry)
            if len(self.logs) > 500:
                self.logs.pop(0)
        self._broadcast("log", log_entry)

    def is_running(self) -> bool:
        with self._lock:
            return self.state["status"] == STATUS_RUNNING

    def _is_active(self, run_id: int) -> bool:
        with self._lock:
            return (
                self._run_id == run_id
                and not self._cancel_requested
                and self.state.get("status") == STATUS_RUNNING
            )

    def get_snapshot(self) -> Dict[str, Any]:
        with self._lock:
            snap = dict(self.state)
            if snap["status"] == STATUS_RUNNING and snap["start_time"]:
                snap["elapsed_seconds"] = int(time.time() - snap["start_time"])
            snap["logs"] = list(self.logs[-100:])
            return snap

    def start(self, batch_size: int = 5, single_test_mode: bool = False):
        """
        Manually trigger a pipeline run.
        Enforces singleton execution and rejects concurrent run requests.
        """
        with self._lock:
            if self.state["status"] == STATUS_RUNNING:
                return False, "Pipeline is already running."

            self._run_id += 1
            current_run_id = self._run_id
            self._cancel_requested = False
            self.logs.clear()
            self.state["status"] = STATUS_RUNNING
            self.state["current_stage"] = 1
            self.state["stage_name"] = "Aggregating RSS Feed"
            self.state["progress_percent"] = 5
            self.state["current_article"] = None
            self.state["start_time"] = time.time()
            self.state["elapsed_seconds"] = 0
            self.state["metrics"] = {
                "evaluated": 0,
                "persisted": 0,
                "irrelevant": 0,
                "skipped": 0,
                "failed": 0,
                "rugs_found": 0,
            }

        self.add_log("INFO", f"Triggered pipeline run (Batch size: {batch_size}, Test mode: {single_test_mode})", run_id=current_run_id)
        self._broadcast("status", self.get_snapshot())

        self._thread = threading.Thread(
            target=self._run_worker,
            args=(current_run_id, batch_size, single_test_mode),
            daemon=True,
        )
        self._thread.start()
        return True, "Pipeline execution started."

    def cancel(self):
        """
        Immediately cancel and halt the running pipeline, allowing instant restart.
        """
        with self._lock:
            if self.state["status"] != STATUS_RUNNING:
                return False, "Pipeline is not currently running."
            self._run_id += 1
            self._cancel_requested = True
            self.state["status"] = STATUS_ABORTED
            if self.state["start_time"]:
                self.state["elapsed_seconds"] = int(time.time() - self.state["start_time"])
        self.add_log("WARN", "Pipeline run stopped by operator.")
        self._broadcast("status", self.get_snapshot())
        return True, "Pipeline execution stopped."

    def _run_worker(self, run_id: int, batch_size: int, single_test_mode: bool):
        try:
            if not self._is_active(run_id):
                return

            # Reload fresh settings from .env with full provider default auto-resolution
            from dotenv import load_dotenv
            from app.config.settings import Settings
            load_dotenv(override=True)
            fresh = Settings()
            settings.database_url = fresh.database_url
            settings.llm_provider = fresh.llm_provider
            settings.llm_api_key = fresh.llm_api_key
            settings.llm_model = fresh.llm_model
            settings.llm_base_url = fresh.llm_base_url
            settings.search_provider = fresh.search_provider
            settings.tavily_api_key = fresh.tavily_api_key
            settings.request_timeout_seconds = fresh.request_timeout_seconds

            # -----------------------------------------------------------------
            # Stage 0: Pre-Flight Configuration & Database Verification
            # -----------------------------------------------------------------
            # 1. Validate Database Configuration
            if not settings.database_url or not settings.database_url.strip():
                self.add_log(
                    "ERROR",
                    "Pre-flight check failed: DATABASE_URL is missing. Please configure your database connection in Settings (⚙️) or .env.",
                    run_id=run_id
                )
                self._finish(STATUS_FAILED, run_id=run_id)
                return

            try:
                # Rebind database engine to current settings.database_url
                from app.storage.database import reset_db_engine
                reset_db_engine(settings.database_url)
                init_db()
            except Exception as db_err:
                self.add_log(
                    "ERROR",
                    f"Pre-flight check failed: Could not connect to database. Details: {db_err}",
                    run_id=run_id
                )
                self._finish(STATUS_FAILED, run_id=run_id)
                return

            # 2. Validate LLM API Key (unless using local Ollama)
            provider = (settings.llm_provider or "gemini").lower().strip()
            if provider != "ollama" and (not settings.llm_api_key or not settings.llm_api_key.strip()):
                self.add_log(
                    "ERROR",
                    f"Pre-flight check failed: Missing LLM API key for provider '{settings.llm_provider}'. Please enter your API key in Settings (⚙️) or .env.",
                    run_id=run_id
                )
                self._finish(STATUS_FAILED, run_id=run_id)
                return

            # 3. Informational Check for Web Search / Tavily
            if (settings.search_provider or "").lower() == "tavily":
                if not settings.tavily_api_key or not settings.tavily_api_key.strip():
                    self.add_log("INFO", "Tavily API key not supplied; defaulting to Mock search for designer verification (zero cost).", run_id=run_id)
                else:
                    self.add_log("INFO", "Tavily live search enabled for designer verification.", run_id=run_id)

            # 4. Custom Base URL (Optional)
            if settings.llm_base_url and settings.llm_base_url.strip():
                self.add_log("INFO", f"Using custom LLM Base URL: {settings.llm_base_url.strip()}", run_id=run_id)

            if not self._is_active(run_id):
                return

            # -----------------------------------------------------------------
            # Stage 1: Fetch RSS
            # -----------------------------------------------------------------
            self._update_stage(1, "Aggregating Architectural Digest India RSS", 10, run_id=run_id)
            self.add_log("STAGE", "[1/6] Connecting to Architectural Digest India RSS feed...", run_id=run_id)
            articles = fetch_rss_feed()
            self.add_log("INFO", f"Fetched {len(articles)} raw articles from RSS feed.", run_id=run_id)

            if not self._is_active(run_id):
                return

            # -----------------------------------------------------------------
            # Stage 2: Deduplication
            # -----------------------------------------------------------------
            self._update_stage(2, "Deduplicating Article Entries", 20, run_id=run_id)
            self.add_log("STAGE", "[2/6] Deduplicating articles via SHA-256 and URL normalization...", run_id=run_id)
            unique_articles = deduplicate_articles(articles)
            self.add_log("INFO", f"Deduplication complete. {len(unique_articles)} unique articles remaining.", run_id=run_id)

            if not self._is_active(run_id):
                return

            # -----------------------------------------------------------------
            # Stage 3: Deterministic Residential Filter
            # -----------------------------------------------------------------
            self._update_stage(3, "Applying Residential Heuristic Filter", 30, run_id=run_id)
            self.add_log("STAGE", "[3/6] Filtering for residential architecture & interior design...", run_id=run_id)
            residential_articles = filter_articles(unique_articles)
            self.add_log("INFO", f"Identified {len(residential_articles)} residential articles.", run_id=run_id)

            if not residential_articles:
                self.add_log("WARN", "No residential articles matched the heuristic filter.", run_id=run_id)
                self._finish(STATUS_COMPLETED, run_id=run_id)
                return

            if not self._is_active(run_id):
                return

            # Determine batch articles from batch size parameter
            limit = 1 if single_test_mode else batch_size
            batch_articles = residential_articles[:limit]
            with self._lock:
                self.state["total_articles"] = len(batch_articles)

            # -----------------------------------------------------------------
            # Stage 4: Multi-Agent Analysis
            # -----------------------------------------------------------------
            self._update_stage(4, "Multi-Agent LangGraph Intelligence Analysis", 35, run_id=run_id)
            self.add_log("STAGE", f"[4/6] Processing {len(batch_articles)} articles with LangGraph agents...", run_id=run_id)

            for idx, article in enumerate(batch_articles, start=1):
                if not self._is_active(run_id):
                    return

                title = article.get("title", "Untitled")
                url = article.get("url", "")
                with self._lock:
                    self.state["current_article"] = {
                        "index": idx,
                        "total": len(batch_articles),
                        "title": title,
                        "url": url,
                    }
                    step_progress = 35 + int((idx / len(batch_articles)) * 45)  # 35% -> 80%
                    self.state["progress_percent"] = step_progress
                    self.state["metrics"]["evaluated"] += 1

                self.add_log("AGENT", f"Article [{idx}/{len(batch_articles)}]: '{title[:65]}...'", run_id=run_id)
                self._broadcast("status", self.get_snapshot())

                try:
                    # 1. Fetch & parse HTML
                    html = fetch_article(url)
                    parsed = parse_article(html)
                    content = parsed.get("text", "")

                    if not self._is_active(run_id):
                        return

                    if not content:
                        self.add_log("WARN", f"Skipped article [{idx}]: empty content extracted.", run_id=run_id)
                        with self._lock:
                            self.state["metrics"]["skipped"] += 1
                        continue

                    # 2. Invoke LangGraph pipeline
                    initial_state = {
                        "run_id": f"ui-run-{idx:03d}",
                        "article_url": url,
                        "article_title": parsed.get("title") or title,
                        "article_summary": parsed.get("description") or article.get("summary") or "",
                        "article_author": parsed.get("author") or article.get("author") or "",
                        "article_published_at": article.get("published"),
                        "article_content": content,
                        "article_content_hash": article.get("content_hash"),
                    }

                    result = graph.invoke(initial_state)

                    if not self._is_active(run_id):
                        return

                    relevant = result.get("article_relevant")
                    status = result.get("status")

                    if not relevant:
                        reason = result.get("relevance_reason", "Not relevant")
                        self.add_log("INFO", f"--> Non-residential / irrelevant: {reason}", run_id=run_id)
                        with self._lock:
                            self.state["metrics"]["irrelevant"] += 1
                    elif status == "persisted":
                        lead_score = result.get("lead_score", 0)
                        rug_score = result.get("rug_score", 0)
                        rug_analysis = result.get("rug_intelligence") or {}
                        with self._lock:
                            if rug_analysis.get("rug_used") or rug_score > 0:
                                self.state["metrics"]["rugs_found"] += 1
                            self.state["metrics"]["persisted"] += 1

                        self.add_log(
                            "SUCCESS",
                            f"--> Qualified Lead Saved to Neon PostgreSQL! (Score: {lead_score}/100, Rug: {rug_score}/100)",
                            run_id=run_id
                        )
                    else:
                        self.add_log("WARN", f"--> Graph status: {status}", run_id=run_id)
                        with self._lock:
                            self.state["metrics"]["failed"] += 1

                except Exception as exc:
                    if not self._is_active(run_id):
                        return
                    err_msg = str(exc)
                    self.add_log("ERROR", f"Error on article [{idx}]: {err_msg}", run_id=run_id)
                    with self._lock:
                        self.state["metrics"]["failed"] += 1

                    # Halt immediately on authentication, invalid API key, or fatal model errors
                    err_lower = err_msg.lower()
                    is_fatal = (
                        isinstance(exc, InvalidConfigurationError)
                        or "invalid llm api key" in err_lower
                        or "invalid api key" in err_lower
                        or "invalid_api_key" in err_lower
                        or "401" in err_msg
                        or "unauthorized" in err_lower
                        or "missing required llm api key" in err_lower
                        or "model_not_found" in err_lower
                        or "model not found" in err_lower
                        or "model unavailable" in err_lower
                        or "quota exceeded" in err_lower
                        or "resource_exhausted" in err_lower
                        or "daily free quota exhausted" in err_lower
                    )
                    if is_fatal:
                        self.add_log("ERROR", "Fatal LLM authentication/configuration error. Halting pipeline execution immediately.", run_id=run_id)
                        self._finish(STATUS_FAILED, run_id=run_id)
                        return

                self._broadcast("status", self.get_snapshot())

                # Responsive sleep: break immediately if canceled or superseded
                for _ in range(30):
                    if not self._is_active(run_id):
                        return
                    time.sleep(0.1)

            if not self._is_active(run_id):
                return

            # If all articles failed in Stage 4, halt and mark pipeline as FAILED
            if self.state["metrics"]["failed"] == len(batch_articles) and len(batch_articles) > 0:
                self.add_log("ERROR", "All articles failed processing. Halting pipeline execution.", run_id=run_id)
                self._finish(STATUS_FAILED, run_id=run_id)
                return

            # -----------------------------------------------------------------
            # Stage 5: Database Persistence Finalized
            # -----------------------------------------------------------------
            self._update_stage(5, "Verifying Neon PostgreSQL Persistence", 85, run_id=run_id)
            self.add_log("STAGE", "[5/6] Database transactions committed to Neon PostgreSQL.", run_id=run_id)

            if not self._is_active(run_id):
                return

            # -----------------------------------------------------------------
            # Stage 6: Excel Export Generation
            # -----------------------------------------------------------------
            self._update_stage(6, "Generating Multi-Sheet Master Excel Report", 92, run_id=run_id)
            self.add_log("STAGE", "[6/6] Generating relationally linked Master Excel workbook...", run_id=run_id)

            db = SessionLocal()
            try:
                exporter = ExcelExporter()
                p_master = exporter.export(db, filename="lead_intelligence_master.xlsx")
                with self._lock:
                    self.state["latest_export_files"] = [str(p_master)]
                self.add_log("SUCCESS", f"Master Export: {p_master.name} ready.", run_id=run_id)
            finally:
                db.close()

            self._finish(STATUS_COMPLETED, run_id=run_id)

        except Exception as exc:
            if not self._is_active(run_id):
                return
            logger.exception("Pipeline run encountered unhandled exception")
            self.add_log("ERROR", f"Pipeline failure: {exc}", run_id=run_id)
            self._finish(STATUS_FAILED, run_id=run_id)

    def _check_cancel(self) -> bool:
        if self._cancel_requested or self.state.get("status") == STATUS_ABORTED:
            return True
        return False

    def _update_stage(self, stage_num: int, stage_name: str, percent: int, run_id: Optional[int] = None):
        with self._lock:
            if run_id is not None and not self._is_active(run_id):
                return
            self.state["current_stage"] = stage_num
            self.state["stage_name"] = stage_name
            self.state["progress_percent"] = percent
        self._broadcast("status", self.get_snapshot())

    def _finish(self, final_status: str, run_id: Optional[int] = None):
        with self._lock:
            if run_id is not None and self._run_id != run_id:
                return
            self.state["status"] = final_status
            if final_status == STATUS_COMPLETED:
                self.state["progress_percent"] = 100
            self.state["current_article"] = None
            if self.state["start_time"]:
                self.state["elapsed_seconds"] = int(time.time() - self.state["start_time"])
        self.add_log("INFO", f"Pipeline run completed with state: {final_status}", run_id=run_id)
        self._broadcast("status", self.get_snapshot())


# Global singleton instance (starts in IDLE state; does NOT execute on load)
runner = PipelineRunner()
