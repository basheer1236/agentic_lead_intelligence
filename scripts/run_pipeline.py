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

    candidates = filter_articles(unique_articles)

    print(f"Residential candidates found: {len(candidates)}")

    if not candidates:
        print("No residential candidates found. Pipeline complete.")
        return

    # -------------------------------------------------
    # 4. Batch candidate processing loop with error isolation
    # -------------------------------------------------

    metrics = {
        "processed": 0,
        "persisted": 0,
        "irrelevant": 0,
        "skipped": 0,
        "failed": 0,
    }

    batch_candidates = candidates[:10]
    batch_limit = len(batch_candidates)

    print(f"\n[4/6] Processing first {len(batch_candidates)} candidate articles after deduplication...")

    for index, article in enumerate(batch_candidates, start=1):
        print(f"\n" + "-" * 50)
        print(f"Processing Article [{index}/{len(batch_candidates)}]")
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
            print(f"--> ERROR processing article: {exc}")
            metrics["failed"] += 1

        if index < len(batch_candidates):
            time.sleep(2)

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
        export_path_std = exporter.export(db, filename="lead_intelligence.xlsx")
        print(f"Excel export generated successfully: {export_path}")
        print(f"Excel export generated successfully: {export_path_std}")
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