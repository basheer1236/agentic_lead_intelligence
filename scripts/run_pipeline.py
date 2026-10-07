import sys
import time

from app.tools.rss_tool import fetch_rss_feed
from app.tools.article_filter import filter_articles
from app.tools.dedup import deduplicate_articles
from app.tools.http_tool import fetch_article
from app.tools.article_parser import parse_article
from app.graph.graph import graph
from app.config.settings import settings


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    print("=" * 60)
    print("AGENTIC LEAD INTELLIGENCE BATCH PIPELINE")
    print("=" * 60)

    # -------------------------------------------------
    # 0. Pre-Flight Configuration Verification
    # -------------------------------------------------
    if not settings.database_url or not settings.database_url.strip():
        print("\n[ERROR] Pipeline halted: Missing DATABASE_URL.")
        print("Please configure DATABASE_URL in your .env file.")
        return

    provider = (settings.llm_provider or "gemini").lower().strip()
    if provider != "ollama" and (not settings.llm_api_key or not settings.llm_api_key.strip()):
        print(f"\n[ERROR] Pipeline halted: Missing API key for provider '{settings.llm_provider}'.")
        print("Please specify LLM_API_KEY in your .env file or Settings.")
        return

    # -------------------------------------------------
    # 1. Fetch RSS
    # -------------------------------------------------

    print("\n[1/6] Fetching Architectural Digest India RSS...")

    articles = fetch_rss_feed()

    print(f"RSS articles found: {len(articles)}")

    # -------------------------------------------------
    # 2. Deduplicate RSS entries
    # -------------------------------------------------

    print("\n[2/6] Deduplicating articles...")

    unique_articles = deduplicate_articles(articles)

    print(f"Unique articles: {len(unique_articles)}")

    # -------------------------------------------------
    # 3. Deterministic residential filtering
    # -------------------------------------------------

    print("\n[3/6] Applying deterministic article filter...")

    residential_articles = filter_articles(unique_articles)

    print(f"Residential articles found: {len(residential_articles)}")

    if not residential_articles:
        print("No residential articles found. Pipeline complete.")
        return

    # -------------------------------------------------
    # 4. Batch article processing loop with error isolation
    # -------------------------------------------------

    # Pre-flight check: validate LLM configuration before executing agents
    provider = (settings.llm_provider or "openai").lower().strip()
    if provider != "ollama" and (not settings.llm_api_key or not settings.llm_api_key.strip()):
        print("\n[ERROR] Pipeline stopped: Missing required LLM API key.")
        print("Please specify LLM_API_KEY in your .env file.")
        return

    metrics = {
        "processed": 0,
        "persisted": 0,
        "irrelevant": 0,
        "skipped": 0,
        "failed": 0,
    }

    batch_articles = residential_articles[:10]
    batch_limit = len(batch_articles)

    print(f"\n[4/6] Processing first {len(batch_articles)} articles after deduplication with LangGraph agents...")

    for index, article in enumerate(batch_articles, start=1):
        print(f"\n" + "-" * 50)
        print(f"Processing Article [{index}/{len(batch_articles)}]")
        print("Title :", article.get("title"))
        print("URL   :", article.get("url"))
        print("-" * 50)

        metrics["processed"] += 1

        try:
            # Fetch & parse content
            html = fetch_article(article["url"])
            parsed = parse_article(html)
            article_content = parsed.get("text", "")

            if not article_content:
                print("--> SKIPPED: Empty content extracted.")
                metrics["skipped"] += 1
                continue

            # Execute LangGraph
            initial_state = {
                "run_id": f"batch-run-{index:03d}",
                "article_url": article.get("url"),
                "article_title": (
                    parsed.get("title")
                    or article.get("title")
                    or ""
                ),
                "article_summary": (
                    parsed.get("description")
                    or article.get("summary")
                    or ""
                ),
                "article_author": (
                    parsed.get("author")
                    or article.get("author")
                ),
                "article_published_at": article.get("published"),
                "article_content": article_content,
                "article_content_hash": article.get("content_hash"),
            }

            result = graph.invoke(initial_state)

            relevant = result.get("article_relevant")
            status = result.get("status")

            if not relevant:
                print(f"--> IRRELEVANT: Reason - {result.get('relevance_reason')}")
                metrics["irrelevant"] += 1
            elif status == "persisted":
                print(f"--> PERSISTED: Lead score={result.get('lead_score')}, Rug score={result.get('rug_score')}")
                metrics["persisted"] += 1
            else:
                print(f"--> FAILED: Graph status = '{status}'")
                metrics["failed"] += 1

        except Exception as exc:
            err_msg = str(exc)
            print(f"--> ERROR processing article: {err_msg}")
            metrics["failed"] += 1

            if "Missing required LLM API key" in err_msg or "InvalidConfigurationError" in err_msg:
                print("\n[ERROR] Fatal LLM configuration error. Halting pipeline execution.")
                return

        if index < len(batch_articles):
            time.sleep(2)

    if metrics["failed"] == len(batch_articles) and len(batch_articles) > 0:
        print("\n[ERROR] All articles failed processing. Halting pipeline.")
        return

    # -------------------------------------------------
    # 5. Export Excel Business Output
    # -------------------------------------------------

    print("\n[5/6] Exporting Excel Business Output...")
    try:
        from app.storage.database import SessionLocal
        from app.export.excel_exporter import ExcelExporter

        db = SessionLocal()
        exporter = ExcelExporter()
        export_path = exporter.export(db, filename="lead_intelligence_master.xlsx")
        print(f"Excel master report generated successfully: {export_path}")
        db.close()
    except Exception as exc:
        print(f"Excel export failed: {exc}")

    # -------------------------------------------------
    # Summary Metrics
    # -------------------------------------------------

    print("\n" + "=" * 60)
    print("BATCH PROCESSING SUMMARY METRICS")
    print("=" * 60)
    print(f"Total Candidates Evaluated : {metrics['processed']}")
    print(f"Successfully Persisted    : {metrics['persisted']}")
    print(f"Irrelevant (Skipped)      : {metrics['irrelevant']}")
    print(f"Content Fetch Skipped     : {metrics['skipped']}")
    print(f"Failed / Errors Isolated  : {metrics['failed']}")
    print("=" * 60)
    print("BATCH PIPELINE EXECUTION COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()