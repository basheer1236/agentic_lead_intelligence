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

    def add_log(self, level: str, message: str):
        now_str = datetime.now().strftime("%H:%M:%S")
        log_entry = {
            "timestamp": now_str,
            "level": level.upper(),
            "message": message,
        }
        with self._lock:
            self.logs.append(log_entry)
            if len(self.logs) > 500:
                self.logs.pop(0)
        self._broadcast("log", log_entry)

    def is_running(self) -> bool:
        with self._lock:
            return self.state["status"] == STATUS_RUNNING

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

        self.add_log("INFO", f"Triggered pipeline run (Batch size: {batch_size}, Test mode: {single_test_mode})")
        self._broadcast("status", self.get_snapshot())

        self._thread = threading.Thread(
            target=self._run_worker,
            args=(batch_size, single_test_mode),
            daemon=True,
        )
        self._thread.start()
        return True, "Pipeline execution started."

    def cancel(self):
        """
        Gracefully request cancellation (abort) of the running pipeline.
        """
        with self._lock:
            if self.state["status"] != STATUS_RUNNING:
                return False, "Pipeline is not running."
            self._cancel_requested = True
        self.add_log("WARN", "Abort signal received from user. Halting pipeline execution...")
        return True, "Abort signal registered."

    def _run_worker(self, batch_size: int, single_test_mode: bool):
        try:
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
            settings.tavily_api_key = fresh.tavily_api_key
            settings.request_timeout_seconds = fresh.request_timeout_seconds

            # Rebind database engine to current settings.database_url
            from app.storage.database import reset_db_engine
            reset_db_engine(settings.database_url)

            # Verify database schema/tables before processing
            init_db()

            # -----------------------------------------------------------------
            # Stage 1: Fetch RSS
            # -----------------------------------------------------------------
            self._update_stage(1, "Aggregating Architectural Digest India RSS", 10)
            self.add_log("STAGE", "[1/6] Connecting to Architectural Digest India RSS feed...")
            articles = fetch_rss_feed()
            self.add_log("INFO", f"Fetched {len(articles)} raw articles from RSS feed.")

            if self._check_cancel():
                return

            # -----------------------------------------------------------------
            # Stage 2: Deduplication
            # -----------------------------------------------------------------
            self._update_stage(2, "Deduplicating Article Entries", 20)
            self.add_log("STAGE", "[2/6] Deduplicating articles via SHA-256 and URL normalization...")
            unique_articles = deduplicate_articles(articles)
            self.add_log("INFO", f"Deduplication complete. {len(unique_articles)} unique articles remaining.")

            if self._check_cancel():
                return

            # -----------------------------------------------------------------
            # Stage 3: Deterministic Residential Filter
            # -----------------------------------------------------------------
            self._update_stage(3, "Applying Residential Heuristic Filter", 30)
            self.add_log("STAGE", "[3/6] Filtering for residential architecture & interior design...")
            residential_articles = filter_articles(unique_articles)
            self.add_log("INFO", f"Identified {len(residential_articles)} residential articles.")

            if not residential_articles:
                self.add_log("WARN", "No residential articles matched the heuristic filter.")
                self._finish(STATUS_COMPLETED)
                return

            # Determine batch articles from batch size parameter
            limit = 1 if single_test_mode else batch_size
            batch_articles = residential_articles[:limit]
            self.state["total_articles"] = len(batch_articles)

            # -----------------------------------------------------------------
            # Stage 4: Multi-Agent Analysis
            # -----------------------------------------------------------------
            self._update_stage(4, "Multi-Agent LangGraph Intelligence Analysis", 35)
            self.add_log("STAGE", f"[4/6] Processing {len(batch_articles)} articles with LangGraph agents...")

            # Pre-flight check: validate LLM configuration before executing agents
            provider = (settings.llm_provider or "openai").lower().strip()
            if provider != "ollama" and (not settings.llm_api_key or not settings.llm_api_key.strip()):
                self.add_log(
                    "ERROR",
                    "Pipeline stopped: Missing required LLM API key. Please configure LLM_API_KEY in Settings or your .env file."
                )
                self._finish(STATUS_FAILED)
                return

            for idx, article in enumerate(batch_articles, start=1):
                if self._check_cancel():
                    return

                title = article.get("title", "Untitled")
                url = article.get("url", "")
                self.state["current_article"] = {
                    "index": idx,
                    "total": len(batch_articles),
                    "title": title,
                    "url": url,
                }
                step_progress = 35 + int((idx / len(batch_articles)) * 45)  # 35% -> 80%
                self.state["progress_percent"] = step_progress

                self.add_log("AGENT", f"Article [{idx}/{len(batch_articles)}]: '{title[:65]}...'")
                self.state["metrics"]["evaluated"] += 1
                self._broadcast("status", self.get_snapshot())

                try:
                    # 1. Fetch & parse HTML
                    html = fetch_article(url)
                    parsed = parse_article(html)
                    content = parsed.get("text", "")

                    if not content:
                        self.add_log("WARN", f"Skipped article [{idx}]: empty content extracted.")
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
                    relevant = result.get("article_relevant")
                    status = result.get("status")

                    if not relevant:
                        reason = result.get("relevance_reason", "Not relevant")
                        self.add_log("INFO", f"--> Non-residential / irrelevant: {reason}")
                        self.state["metrics"]["irrelevant"] += 1
                    elif status == "persisted":
                        lead_score = result.get("lead_score", 0)
                        rug_score = result.get("rug_score", 0)
                        rug_analysis = result.get("rug_intelligence") or {}
                        if rug_analysis.get("rug_used") or rug_score > 0:
                            self.state["metrics"]["rugs_found"] += 1

                        self.add_log(
                            "SUCCESS",
                            f"--> Qualified Lead Saved to Neon PostgreSQL! (Score: {lead_score}/100, Rug: {rug_score}/100)",
                        )
                        self.state["metrics"]["persisted"] += 1
                    else:
                        self.add_log("WARN", f"--> Graph status: {status}")
                        self.state["metrics"]["failed"] += 1

                except Exception as exc:
                    err_msg = str(exc)
                    self.add_log("ERROR", f"Error on article [{idx}]: {err_msg}")
                    self.state["metrics"]["failed"] += 1

                    # If missing API key or fatal configuration error, halt pipeline immediately
                    if "Missing required LLM API key" in err_msg or "InvalidConfigurationError" in err_msg:
                        self.add_log("ERROR", "Fatal LLM configuration error. Halting pipeline execution.")
                        self._finish(STATUS_FAILED)
                        return

                self._broadcast("status", self.get_snapshot())
                time.sleep(3)

            # If all articles failed in Stage 4, halt and mark pipeline as FAILED
            if self.state["metrics"]["failed"] == len(batch_articles) and len(batch_articles) > 0:
                self.add_log("ERROR", "All articles failed processing. Halting pipeline execution.")
                self._finish(STATUS_FAILED)
                return

            # -----------------------------------------------------------------
            # Stage 5: Database Persistence Finalized
            # -----------------------------------------------------------------
            self._update_stage(5, "Verifying Neon PostgreSQL Persistence", 85)
            self.add_log("STAGE", "[5/6] Database transactions committed to Neon PostgreSQL.")

            # -----------------------------------------------------------------
            # Stage 6: Excel Export Generation
            # -----------------------------------------------------------------
            self._update_stage(6, "Generating Multi-Sheet Master Excel Report", 92)
            self.add_log("STAGE", "[6/6] Generating relationally linked Excel workbooks...")

            db = SessionLocal()
            try:
                exporter = ExcelExporter()
                p_master = exporter.export(db, filename="lead_intelligence_master.xlsx")
                p_std = exporter.export(db, filename="lead_intelligence.xlsx")
                self.state["latest_export_files"] = [str(p_master), str(p_std)]
                self.add_log("SUCCESS", f"Master Export: {p_master.name} ready.")
                self.add_log("SUCCESS", f"Standard Export: {p_std.name} ready.")
            finally:
                db.close()

            self._finish(STATUS_COMPLETED)

        except Exception as exc:
            logger.exception("Pipeline run encountered unhandled exception")
            self.add_log("ERROR", f"Pipeline failure: {exc}")
            self._finish(STATUS_FAILED)

    def _check_cancel(self) -> bool:
        if self._cancel_requested:
            self.add_log("WARN", "Pipeline run aborted by operator.")
            self._finish(STATUS_ABORTED)
            return True
        return False

    def _update_stage(self, stage_num: int, stage_name: str, percent: int):
        with self._lock:
            self.state["current_stage"] = stage_num
            self.state["stage_name"] = stage_name
            self.state["progress_percent"] = percent
        self._broadcast("status", self.get_snapshot())

    def _finish(self, final_status: str):
        with self._lock:
            self.state["status"] = final_status
            if final_status == STATUS_COMPLETED:
                self.state["progress_percent"] = 100
            self.state["current_article"] = None
            if self.state["start_time"]:
                self.state["elapsed_seconds"] = int(time.time() - self.state["start_time"])
        self.add_log("INFO", f"Pipeline run completed with state: {final_status}")
        self._broadcast("status", self.get_snapshot())


# Global singleton instance (starts in IDLE state; does NOT execute on load)
runner = PipelineRunner()
