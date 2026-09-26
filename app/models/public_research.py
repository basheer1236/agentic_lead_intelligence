from typing import Optional

from pydantic import BaseModel, Field


class ResearchSource(BaseModel):

    title: str

    url: str

    source_type: str

    relevance: bool

    confidence: float = Field(
        ge=0.0,
        le=1.0,
    )

    reason: str

    evidence: Optional[str] = None


class PublicResearchResult(BaseModel):

    designer_name: str

    studio_name: Optional[str] = None

    sources: list[ResearchSource] = Field(
        default_factory=list
    )