from datetime import datetime, timezone

from app.config.settings import settings
from app.utils.logger import log_telemetry, ExecutionTimer
from app.agents.relevance_agent import RelevanceAgent
from app.agents.project_agent import ProjectIntelligenceAgent
from app.agents.rug_agent import RugIntelligenceAgent
from app.agents.designer_resolver import DesignerResolver
from app.agents.lead_intelligence import LeadIntelligenceAgent
from app.agents.freshness_manager import get_freshness_status
from app.agents.enrichment_gate import decide_enrichment_action
from app.tools.designer_profile_tool import fetch_designer_profile
from app.agents.designer_enrichment import DesignerEnrichmentAgent
from app.tools.public_search_tool import create_search_tool
from app.agents.public_research_agent import PublicResearchAgent
from app.tools.public_source_tool import fetch_public_source
from app.agents.designer_enrichment_pipeline import DesignerEnrichmentPipeline
from app.agents.designer_enrichment_merge import merge_designer_enrichment
from app.models.source_extraction import ExtractedField

from app.storage.database import SessionLocal
from app.storage.repositories.designer_repository import DesignerRepository
from app.storage.persistence.pipeline_persistence import PipelinePersistenceService


# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------

def _list_to_text(values):
    """
    Convert a list of strings into a database-friendly string.
    """
    if not values:
        return None

    return ", ".join(str(value) for value in values)


def _normalize_rug_used(value):
    """
    Convert the LLM's Yes/No/Unclear or boolean output into
    the Boolean representation used by PostgreSQL.
    """
    if value is None:
        return None

    if isinstance(value, bool):
        return value

    normalized = str(value).strip().lower()

    if normalized in ("yes", "true", "1"):
        return True

    if normalized in ("no", "false", "0"):
        return False

    # Unclear cannot safely become True or False.
    return None


def _parse_published_at(val):
    """
    Safely parse published_at into a datetime object if it is a string.
    """
    if val is None:
        return None

    if isinstance(val, datetime):
        return val

    if isinstance(val, str) and val.strip():
        for fmt in (
            "%Y-%m-%d",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%S%z",
            "%a, %d %b %Y %H:%M:%S %z",
            "%a, %d %b %Y %H:%M:%S GMT",
        ):
            try:
                return datetime.strptime(val.strip(), fmt)
            except ValueError:
                pass

    return None


# ---------------------------------------------------------
# Node 1 — Initialize
# ---------------------------------------------------------

def initialize_node(state):
    return {
        "status": "initialized",
        "iteration_count": 0,
        "errors": [],
        "tool_results": [],
        "evidence": [],
        "rug_mentions": [],
    }


# ---------------------------------------------------------
# Node 2 — Article Relevance
# ---------------------------------------------------------

def relevance_node(state):
    with ExecutionTimer("relevance") as timer:
        agent = RelevanceAgent()

        result = agent.classify(
            title=state.get("article_title", ""),
            description=state.get("article_summary", ""),
            text=state.get("article_content", ""),
        )

        log_telemetry(
            "node_completed",
            node="relevance",
            run_id=state.get("run_id"),
            article_url=state.get("article_url"),
            is_relevant=result.is_relevant,
            confidence=result.confidence,
            duration_seconds=timer.duration,
        )

    return {
        "article_relevant": result.is_relevant,
        "relevance_score": result.confidence,
        "relevance_reason": result.reason,
        "status": "relevance_completed",
    }


# ---------------------------------------------------------
# Node 3 — Project Intelligence
# ---------------------------------------------------------

def project_node(state):
    agent = ProjectIntelligenceAgent()

    result = agent.extract(
        title=state.get("article_title", ""),
        text=state.get("article_content", ""),
    )

    homeowner = {
        "name": result.homeowner.name if result.homeowner else None,
        "profession": result.homeowner.profession if result.homeowner else None,
        "industry": result.homeowner.industry if result.homeowner else None,
        "city": result.homeowner.city if result.homeowner else None,
        "country": result.homeowner.country if result.homeowner else None,
        "public_profile_mentioned": (
            str(result.homeowner.public_profile_mentioned)
            if result.homeowner and result.homeowner.public_profile_mentioned is not None
            else None
        ),
    }

    designer = {
        "name": result.designer.name if result.designer else None,
        "studio": result.designer.studio if result.designer else None,
        "project_role": result.designer.project_role if result.designer else None,
        "city": result.designer.city if result.designer else None,
        "website": result.designer.website if result.designer else None,
        "project_mention": (
            str(result.designer.project_mention)
            if result.designer and result.designer.project_mention is not None
            else None
        ),
    }

    project = {
        "project_name": result.project_name,
        "home_type": result.home_type,
        "location": result.location,
        "project_size": result.project_size,
        "completion_year": (
            str(result.completion_year)
            if result.completion_year is not None
            else None
        ),
    }

    materials = {
        "flooring": result.flooring,
        "furniture": result.furniture,
        "decor": result.decor,
        "textile_elements": result.textile_elements,
        "sourcing_notes": result.sourcing_notes,
    }

    return {
        "project": project,
        "homeowner": homeowner,
        "designer": designer,
        "materials": materials,
        "status": "project_extraction_completed",
    }


# ---------------------------------------------------------
# Node 4 — Rug Intelligence
# ---------------------------------------------------------

def rug_node(state):
    agent = RugIntelligenceAgent()

    result = agent.analyze(
        title=state.get("article_title", ""),
        text=state.get("article_content", ""),
    )

    rug_used = _normalize_rug_used(result.rug_used)

    rug = {
        "rug_used": rug_used,
        "rug_type": result.rug_type,
        "rug_origin": result.rug_origin,
        "rug_material": result.rug_material,
        "rug_supplier": result.rug_supplier,
        "rug_brand": result.rug_brand,
        "handmade": result.handmade,
        "handwoven": result.handwoven,
        "vintage": result.vintage,
        "custom_made": result.custom_made,
        "imported": result.imported,
        "designer_custom_rug": result.designer_custom_rug,
        "matched_keywords": result.matched_keywords,
        "multiple_rugs": result.multiple_rugs,
        "luxury_project": result.luxury_project,
        "room_location": result.room_location,
        "rug_notes": result.rug_notes,
    }

    return {
        "rug_mentions": [rug],
        "status": "rug_analysis_completed",
    }


# ---------------------------------------------------------
# Node 5 — Designer Resolution
# ---------------------------------------------------------

def designer_resolution_node(state):
    designer = state.get("designer", {})

    designer_name = designer.get("name")
    studio_name = designer.get("studio")

    resolver = DesignerResolver()

    result = resolver.resolve(
        designer_name=designer_name,
        studio_name=studio_name,
    )

    tool_results = list(state.get("tool_results", []))
    tool_results.append({
        "tool": "designer_resolver",
        "result": result,
    })

    return {
        "designer_match_type": result.get("match_type"),
        "designer_profile_url": result.get("profile_url"),
        "designer_id": result.get("matched_name"),
        "tool_results": tool_results,
        "status": "designer_resolution_completed",
    }


# ---------------------------------------------------------
# Node 5.1 — Enrichment Gate Routing
# ---------------------------------------------------------

def route_enrichment_gate(state):
    designer = state.get("designer", {})
    designer_name = designer.get("name")
    studio_name = designer.get("studio")

    if not designer_name and not studio_name:
        return "skip_enrichment"

    norm_name = designer_name.strip().lower() if designer_name else None
    website = designer.get("website")

    db = SessionLocal()
    existing_designer = None
    try:
        if norm_name:
            existing_designer = DesignerRepository.get_by_normalized_name(
                db=db, normalized_name=norm_name
            )
        if not existing_designer and website:
            existing_designer = DesignerRepository.get_by_website(
                db=db, website=website
            )

        last_enriched_at = (
            existing_designer.last_enriched_at if existing_designer else None
        )
        freshness_status = get_freshness_status(last_enriched_at)
        enrichment_action = decide_enrichment_action(freshness_status)

        if enrichment_action == "REUSE_EXISTING":
            return "skip_enrichment"
        else:
            return "enrich_designer"
    except Exception:
        return "enrich_designer"
    finally:
        db.close()


# ---------------------------------------------------------
# Node 5.2 — Designer Enrichment Node
# ---------------------------------------------------------

def designer_enrichment_node(state):
    designer = dict(state.get("designer", {}))
    designer_name = designer.get("name")
    studio_name = designer.get("studio")

    profile_url = state.get("designer_profile_url")

    ad_enrichment = None
    if profile_url:
        try:
            profile_data = fetch_designer_profile(profile_url)
            ad_agent = DesignerEnrichmentAgent()
            ad_enrichment = ad_agent.enrich(
                designer_name=designer_name,
                studio_name=studio_name,
                profile=profile_data,
            )
        except Exception as exc:
            print(f"[designer_enrichment_node] AD PRO profile error: {exc}")

    web_enrichment = None
    if getattr(settings, "tavily_api_key", None):
        query = f"{designer_name or ''} {studio_name or ''} interior design".strip()
        if query:
            try:
                search_tool = create_search_tool()
                raw_results = search_tool.search(query, max_results=5)
                research_agent = PublicResearchAgent()
                research_res = research_agent.research(
                    designer_name=designer_name or "",
                    studio_name=studio_name or "",
                    search_results=raw_results,
                )
                relevant_sources = []
                for src in research_res.sources:
                    if src.relevance and src.url:
                        try:
                            source_data = fetch_public_source(src.url)
                            relevant_sources.append(source_data)
                        except Exception:
                            pass
                if relevant_sources:
                    pipeline = DesignerEnrichmentPipeline()
                    web_enrichment = pipeline.process_sources(
                        designer_name=designer_name or "",
                        studio_name=studio_name or "",
                        sources=relevant_sources,
                    )
            except Exception as exc:
                print(f"[designer_enrichment_node] Web research error: {exc}")

    final_enrichment = None
    if ad_enrichment and web_enrichment:
        final_enrichment = merge_designer_enrichment(ad_enrichment, web_enrichment)
    elif ad_enrichment:
        final_enrichment = ad_enrichment
    elif web_enrichment:
        final_enrichment = web_enrichment

    evidence_list = []
    if final_enrichment:
        if final_enrichment.website:
            designer["website"] = final_enrichment.website
        if final_enrichment.address:
            designer["address"] = final_enrichment.address
        if final_enrichment.city:
            designer["city"] = final_enrichment.city
        if final_enrichment.country:
            designer["country"] = final_enrichment.country
        if final_enrichment.contact:
            designer["contact"] = final_enrichment.contact
        if final_enrichment.email:
            designer["email"] = final_enrichment.email
        if final_enrichment.company_description:
            designer["description"] = final_enrichment.company_description
        if final_enrichment.linkedin_url:
            designer["linkedin_url"] = final_enrichment.linkedin_url
        if final_enrichment.instagram_url:
            designer["instagram_url"] = final_enrichment.instagram_url
        if final_enrichment.facebook_url:
            designer["facebook_url"] = final_enrichment.facebook_url
        if final_enrichment.youtube_url:
            designer["youtube_url"] = final_enrichment.youtube_url

        evidence_list = [e.model_dump() for e in final_enrichment.evidence]

    return {
        "designer": designer,
        "evidence": evidence_list,
        "enrichment_status": state.get("enrichment_status") or "FRESH",
        "status": "designer_enrichment_completed",
    }


# ---------------------------------------------------------
# Node 6 — Lead Intelligence / Scoring
# ---------------------------------------------------------

def lead_intelligence_node(state):
    agent = LeadIntelligenceAgent()

    designer = state.get("designer", {})
    rug_mentions = state.get("rug_mentions", [])

    rug = rug_mentions[0] if rug_mentions else {}

    supplier_mentioned = bool(rug.get("rug_supplier"))

    multiple_projects = bool(rug.get("multiple_rugs"))

    active_social = bool(
        designer.get("linkedin_url")
        or designer.get("instagram_url")
        or designer.get("facebook_url")
        or designer.get("youtube_url")
    )
    contact_data = bool(
        designer.get("email")
        or designer.get("contact")
        or designer.get("phone")
    )

    result = agent.analyze(
        designer_name=designer.get("name"),
        studio_name=designer.get("studio"),
        last_enriched_at=None,
        featured_in_ad=True,
        luxury_residence=bool(rug.get("luxury_project")),
        rug=rug,
        supplier_mentioned=supplier_mentioned,
        multiple_projects=multiple_projects,
        active_social=active_social,
        contact_data=contact_data,
    )

    return {
        "enrichment_status": result.freshness_status,
        "lead_score": result.lead_score,
        "rug_score": result.rug_opportunity_score,
        "status": "lead_intelligence_completed",
    }


# ---------------------------------------------------------
# Node 7 — Persistence
# ---------------------------------------------------------

def persistence_node(state):
    db = SessionLocal()

    try:
        # ---------------------------------------------
        # Article
        # ---------------------------------------------

        published_at_parsed = _parse_published_at(
            state.get("article_published_at")
        )

        article, article_created = PipelinePersistenceService.save_article(
            db=db,
            url=state.get("article_url"),
            title=state.get("article_title"),
            author=state.get("article_author"),
            summary=state.get("article_summary"),
            published_at=published_at_parsed,
            content_hash=state.get("article_content_hash"),
        )

        # ---------------------------------------------
        # Project
        # ---------------------------------------------

        project_data = state.get("project", {})
        homeowner = state.get("homeowner", {})
        designer = state.get("designer", {})
        materials = state.get("materials", {})

        # ---------------------------------------------
        # Designer
        # ---------------------------------------------

        designer_record = None
        designer_created = False

        if designer.get("name"):
            from app.utils.name_normalizer import normalize_designer_name
            canonical_name = normalize_designer_name(designer.get("name"))

            designer_record, designer_created = (
                PipelinePersistenceService.save_designer(
                    db=db,
                    designer_name=designer.get("name"),
                    studio_name=designer.get("studio"),
                    normalized_name=canonical_name,
                    website=designer.get("website"),
                    address=designer.get("address"),
                    city=designer.get("city"),
                    country=designer.get("country"),
                    contact=designer.get("contact"),
                    email=designer.get("email"),
                    company_description=designer.get("description"),
                    linkedin_url=designer.get("linkedin_url"),
                    instagram_url=designer.get("instagram_url"),
                    facebook_url=designer.get("facebook_url"),
                    youtube_url=designer.get("youtube_url"),
                    last_enriched_at=datetime.now(timezone.utc),
                )
            )

            # Persist evidence to sources table
            evidence_data = state.get("evidence", [])
            if evidence_data and designer_record:
                extracted_fields = [
                    ExtractedField(
                        field=e.get("field", "unknown"),
                        value=e.get("value"),
                        source_url=e.get("source_url", ""),
                        source_type=e.get("source_type", "unknown"),
                        evidence_text=e.get("evidence_text"),
                        confidence=e.get("confidence", 1.0),
                    )
                    for e in evidence_data
                ]
                PipelinePersistenceService.save_evidence(
                    db=db,
                    designer_id=designer_record.id,
                    extracted_fields=extracted_fields,
                )

        # ---------------------------------------------
        # Project
        # ---------------------------------------------

        project = PipelinePersistenceService.save_project(
            db=db,
            article_id=article.id,
            designer_id=designer_record.id if designer_record else None,
            project_name=project_data.get("project_name"),
            home_type=project_data.get("home_type"),
            location=project_data.get("location"),
            project_size=project_data.get("project_size"),
            completion_year=project_data.get("completion_year"),

            homeowner_name=homeowner.get("name"),
            homeowner_profession=homeowner.get("profession"),
            homeowner_industry=homeowner.get("industry"),
            homeowner_city=homeowner.get("city"),
            homeowner_country=homeowner.get("country"),

            designer_name=designer.get("name"),
            designer_studio=designer.get("studio"),
            designer_role=designer.get("project_role"),
            designer_city=designer.get("city"),
            designer_website=designer.get("website"),

            flooring=_list_to_text(materials.get("flooring")),
            furniture=_list_to_text(materials.get("furniture")),
            decor=_list_to_text(materials.get("decor")),
            textile_elements=_list_to_text(
                materials.get("textile_elements")
            ),
            sourcing_notes=_list_to_text(
                materials.get("sourcing_notes")
            ),
        )

        # ---------------------------------------------
        # Rug
        # ---------------------------------------------

        rug_record = None

        rug_mentions = state.get("rug_mentions", [])

        if rug_mentions:
            rug = rug_mentions[0]

            rug_record = PipelinePersistenceService.save_rug(
                db=db,
                project_id=project.id,
                designer_id=designer_record.id if designer_record else project.designer_id,
                rug_used=rug.get("rug_used"),
                rug_type=rug.get("rug_type"),
                origin=rug.get("rug_origin"),
                material=rug.get("rug_material"),
                supplier=rug.get("rug_supplier"),
                brand=rug.get("rug_brand"),
                handmade=rug.get("handmade"),
                handwoven=rug.get("handwoven"),
                vintage=rug.get("vintage"),
                custom_made=rug.get("custom_made"),
                imported=rug.get("imported"),
                designer_custom_rug=rug.get("designer_custom_rug"),
                matched_keywords=rug.get("matched_keywords"),
                sourcing_notes=rug.get("rug_notes"),
                opportunity_score=state.get("rug_score"),
            )

        # ---------------------------------------------
        # Scores
        # ---------------------------------------------

        score_record = PipelinePersistenceService.save_scores(
            db=db,
            project_id=project.id,
            lead_score=state.get("lead_score"),
            rug_opportunity_score=state.get("rug_score"),
        )

        log_telemetry(
            "node_completed",
            node="persistence",
            run_id=state.get("run_id"),
            article_url=state.get("article_url"),
            article_id=article.id,
            project_id=project.id,
            designer_id=designer_record.id if designer_record else None,
            lead_score=state.get("lead_score"),
            rug_score=state.get("rug_score"),
            status="persisted",
        )

        return {
            "status": "persisted",
            "designer_db_id": (
                designer_record.id if designer_record else None
            ),
            "tool_results": state.get("tool_results", []) + [
                {
                    "tool": "postgresql_persistence",
                    "article_id": article.id,
                    "article_created": article_created,
                    "project_id": project.id,
                    "designer_id": (
                        designer_record.id
                        if designer_record
                        else None
                    ),
                    "designer_created": designer_created,
                    "rug_id": (
                        rug_record.id
                        if rug_record
                        else None
                    ),
                    "score_id": score_record.id,
                }
            ],
        }

    except Exception as exc:
        db.rollback()

        return {
            "status": "persistence_failed",
            "errors": state.get("errors", []) + [
                {
                    "stage": "persistence",
                    "error": str(exc),
                }
            ],
        }

    finally:
        db.close()