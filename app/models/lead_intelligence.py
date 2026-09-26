from typing import Literal, Optional

from pydantic import BaseModel, Field


class LeadIntelligence(BaseModel):
    designer_name: Optional[str] = None
    studio_name: Optional[str] = None

    freshness_status: Literal[
        "NEW",
        "FRESH",
        "STALE",
    ]

    enrichment_action: Literal[
        "RUN_FULL_ENRICHMENT",
        "REFRESH_ENRICHMENT",
        "REUSE_EXISTING",
    ]

    lead_score: int = Field(
        ge=0,
        le=100,
    )

    rug_opportunity_score: int = Field(
        ge=0,
        le=100,
    )

    rug_used: str | bool | None = None

    supplier_mentioned: bool = False
    multiple_projects: bool = False
    active_social: bool = False
    contact_data: bool = False