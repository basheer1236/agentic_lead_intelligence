from typing import Any, TypedDict


class LeadIntelligenceState(TypedDict, total=False):
    run_id: str
    status: str
    iteration_count: int

    article_url: str
    article_title: str
    article_summary: str
    article_author: str
    article_published_at: Any
    article_content: str
    article_content_hash: str

    article_relevant: bool
    relevance_score: float
    relevance_reason: str

    project: dict[str, Any]
    homeowner: dict[str, Any]
    designer: dict[str, Any]
    materials: dict[str, Any]

    rug_mentions: list[dict[str, Any]]

    designer_id: str | None
    designer_profile_url: str | None
    designer_db_id: int | None
    designer_match_type: str | None

    enrichment_status: str | None

    research_targets: list[str]
    fetched_sources: list[dict[str, Any]]
    evidence: list[dict[str, Any]]

    rug_score: int
    lead_score: int

    tool_results: list[dict[str, Any]]
    errors: list[dict[str, Any]]