"""
Enrich Missing Designers Script
--------------------------------
Identifies designers in the database / Excel master where website or contact
details are 'Not Disclosed' or missing.

Fetches the designer name and designer studio name, first checks AD PRO Directory,
and if site details are not available in AD PRO, searches using the Public Search Agent
(DuckDuckGo Search) to crawl their official studio website and subpages (/about, /contact, /info).

Persists all extracted site details into Neon PostgreSQL and exports a refreshed
master Excel report with unmasked URLs.

Usage:
    python scripts/enrich_missing_designers.py
    python scripts/enrich_missing_designers.py --all
    python scripts/enrich_missing_designers.py --id 37
"""

import sys
import os
import argparse
from urllib.parse import urlparse
from datetime import datetime, timezone
from sqlalchemy import text

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.config.settings import settings
from app.storage.database import SessionLocal
from app.storage.models.designer import DesignerDB
from app.storage.models.project import ProjectDB
from app.storage.persistence.pipeline_persistence import PipelinePersistenceService
from app.agents.designer_resolver import DesignerResolver
from app.tools.designer_profile_tool import fetch_designer_profile
from app.agents.designer_enrichment import DesignerEnrichmentAgent
from app.tools.public_search_tool import create_search_tool
from app.agents.public_research_agent import PublicResearchAgent
from app.tools.public_source_tool import fetch_public_source
from app.agents.designer_enrichment_pipeline import DesignerEnrichmentPipeline
from app.agents.designer_enrichment_merge import merge_designer_enrichment
from app.graph.nodes import _is_official_studio_domain
from app.export.excel_exporter import ExcelExporter
from app.models.public_research import ResearchSource


def enrich_single_designer(designer_name: str, studio_name: str | None) -> dict:
    """
    Enrich a designer by name and studio:
    1. Check AD PRO Directory.
    2. If website not available, search using Public Search Agent (DuckDuckGo).
    3. Deep-crawl homepage, /about, /contact, /info pages on official domain.
    4. Return resolved attributes dict.
    """
    designer_name = (designer_name or "").strip()
    studio_name = (studio_name or "").strip() or None

    print(f"\n{'=' * 65}")
    print(f"Target Designer : {designer_name}")
    print(f"Target Studio   : {studio_name or 'N/A'}")
    print(f"{'=' * 65}")

    # 1. Resolve against AD PRO Directory
    resolver = DesignerResolver()
    res = resolver.resolve(designer_name=designer_name, studio_name=studio_name)
    profile_url = res.get("profile_url")

    ad_enrichment = None
    if profile_url:
        print(f"--> Found AD PRO Directory Profile: {profile_url}")
        try:
            profile_data = fetch_designer_profile(profile_url)
            ad_agent = DesignerEnrichmentAgent()
            ad_enrichment = ad_agent.enrich(
                designer_name=designer_name,
                studio_name=studio_name,
                profile=profile_data,
            )
        except Exception as exc:
            print(f"--> AD PRO fetch error: {exc}")
    else:
        print("--> Not available in AD PRO Directory. Falling back to Public Search Agent...")

    # 2. Check if Public Web Search is needed (e.g. if AD PRO is missing website or missing entirely)
    needs_web_search = True
    if ad_enrichment and ad_enrichment.website:
        needs_web_search = False
        print(f"--> AD PRO already provided website: {ad_enrichment.website}")

    web_enrichment = None
    if needs_web_search:
        query = " ".join(f"{designer_name} {studio_name or ''} interior design".split())
        print(f"--> Public Search Agent Query: '{query}'")

        try:
            search_tool = create_search_tool()
            raw_results = search_tool.search(query, max_results=5)
            print(f"--> Retrieved {len(raw_results)} web search results.")

            research_agent = PublicResearchAgent()
            research_res = research_agent.research(
                designer_name=designer_name,
                studio_name=studio_name or "",
                search_results=raw_results,
            )

            # Deterministic official domain guarantee: ensure official studio domain is never missed
            for res_item in raw_results:
                res_url = res_item.get("url") or ""
                p_res = urlparse(res_url)
                if p_res.netloc and _is_official_studio_domain(p_res.netloc, designer_name, studio_name):
                    if not any(getattr(s, "url", None) == res_url for s in research_res.sources):
                        research_res.sources.insert(0, ResearchSource(
                            title=res_item.get("title", ""),
                            url=res_url,
                            source_type="public_web_search",
                            relevance=True,
                            confidence=0.95,
                            reason="Deterministic official studio domain match",
                            evidence=res_item.get("snippet", "")
                        ))

            relevant_sources = []
            visited_urls = set()
            discovered_subpages = []

            for src in research_res.sources:
                if src.relevance and src.url:
                    clean_u = src.url.split("#")[0].rstrip("/")
                    if clean_u in visited_urls:
                        continue
                    visited_urls.add(clean_u)
                    try:
                        print(f"--> Crawling source: {clean_u}")
                        source_data = fetch_public_source(src.url)
                        source_data["requested_url"] = src.url
                        relevant_sources.append(source_data)

                        parsed = urlparse(src.url)
                        netloc = parsed.netloc.lower()
                        if netloc and _is_official_studio_domain(netloc, designer_name, studio_name):
                            for page_list in (source_data.get("about_pages", [])[:2], source_data.get("contact_pages", [])[:2]):
                                for subpage_url in page_list:
                                    clean_sub = subpage_url.split("#")[0].rstrip("/")
                                    if clean_sub not in visited_urls and clean_sub not in discovered_subpages:
                                        discovered_subpages.append(clean_sub)
                                        visited_urls.add(clean_sub)
                    except Exception as exc:
                        print(f"--> Source crawl error ({src.url}): {exc}")

            for subpage_url in [u for u in discovered_subpages if u.startswith(("http://", "https://"))]:
                try:
                    print(f"--> Deep-crawling studio subpage: {subpage_url}")
                    subpage_data = fetch_public_source(subpage_url)
                    subpage_data["requested_url"] = subpage_url
                    relevant_sources.append(subpage_data)
                except Exception as exc:
                    print(f"--> Subpage crawl error ({subpage_url}): {exc}")

            if relevant_sources:
                pipeline = DesignerEnrichmentPipeline()
                web_enrichment = pipeline.process_sources(
                    designer_name=designer_name,
                    studio_name=studio_name or "",
                    sources=relevant_sources,
                )
        except Exception as exc:
            print(f"--> Public Search Agent error: {exc}")

    # 3. Merge AD PRO & Web Enrichment
    final_enrichment = None
    if ad_enrichment and web_enrichment:
        final_enrichment = merge_designer_enrichment(ad_enrichment, web_enrichment)
    elif ad_enrichment:
        final_enrichment = ad_enrichment
    elif web_enrichment:
        final_enrichment = web_enrichment

    result = {}
    if final_enrichment:
        result["website"] = final_enrichment.website
        result["contact"] = final_enrichment.contact
        result["email"] = final_enrichment.email
        result["address"] = final_enrichment.address
        result["city"] = final_enrichment.city
        result["country"] = final_enrichment.country or "India"
        result["company_description"] = final_enrichment.company_description
        result["instagram_url"] = final_enrichment.instagram_url
        result["facebook_url"] = final_enrichment.facebook_url
        result["linkedin_url"] = final_enrichment.linkedin_url
        result["youtube_url"] = final_enrichment.youtube_url

    return result


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="Enrich missing designers using Public Search Agent")
    parser.add_argument("--all", action="store_true", help="Enrich all designers regardless of current website status")
    parser.add_argument("--id", type=int, help="Enrich a specific designer ID")
    args = parser.parse_args()

    print("=" * 65)
    print("UNIVERSAL DESIGNER RE-ENRICHMENT PIPELINE")
    print("=" * 65)

    with SessionLocal() as db:
        query = db.query(DesignerDB)
        if args.id:
            query = query.filter(DesignerDB.id == args.id)
        elif not args.all:
            # Only designers where website is missing or Not Disclosed
            query = query.filter(
                (DesignerDB.website.is_(None))
                | (DesignerDB.website == "")
                | (DesignerDB.website.ilike("not disclosed"))
                | (DesignerDB.contact.is_(None))
                | (DesignerDB.contact.ilike("not disclosed"))
            )

        designer_targets = [
            {"id": d.id, "name": d.designer_name, "studio": d.studio_name}
            for d in query.order_by(DesignerDB.id.asc()).all()
        ]

    print(f"Designers identified for enrichment: {len(designer_targets)}")

    if not designer_targets:
        print("All designers are already fully enriched with site details!")
        return

    enriched_count = 0
    for i, target in enumerate(designer_targets, start=1):
        d_id = target["id"]
        d_name = target["name"]
        d_studio = target["studio"]

        print(f"\n[{i}/{len(designer_targets)}] Processing Designer ID {d_id}: {d_name} ({d_studio})")
        details = enrich_single_designer(d_name, d_studio)

        if details:
            with SessionLocal() as db:
                d = db.query(DesignerDB).filter(DesignerDB.id == d_id).first()
                if not d:
                    continue

                if details.get("website"):
                    d.website = details["website"]
                if details.get("contact"):
                    d.contact = details["contact"]
                if details.get("email"):
                    d.email = details["email"]
                if details.get("address"):
                    d.address = details["address"]
                if details.get("city"):
                    d.city = details["city"]
                if details.get("country"):
                    d.country = details["country"]
                if details.get("company_description"):
                    d.company_description = details["company_description"]
                if details.get("instagram_url"):
                    d.instagram_url = details["instagram_url"]
                if details.get("facebook_url"):
                    d.facebook_url = details["facebook_url"]
                if details.get("linkedin_url"):
                    d.linkedin_url = details["linkedin_url"]
                if details.get("youtube_url"):
                    d.youtube_url = details["youtube_url"]

                d.last_enriched_at = datetime.now(timezone.utc)

                # Also update corresponding project records
                projects = db.query(ProjectDB).filter(ProjectDB.designer_id == d_id).all()
                for p in projects:
                    if details.get("website"):
                        p.designer_website = details["website"]
                    if details.get("city"):
                        p.designer_city = details["city"]

                db.commit()
                enriched_count += 1
                print(f"--> Saved to Database: Website={d.website}, Contact={d.contact}, Email={d.email}")

    # Regenerate Excel Master Export
    print(f"\n{'=' * 65}")
    print("EXPORTING UPDATED EXCEL MASTER REPORT...")
    print(f"{'=' * 65}")
    with SessionLocal() as db:
        exporter = ExcelExporter()
        export_path = exporter.export(db, filename="lead_intelligence_master.xlsx")
        print(f"Excel report updated successfully: {export_path}")
        print(f"Total designers successfully enriched: {enriched_count}/{len(designer_targets)}")


if __name__ == "__main__":
    main()
