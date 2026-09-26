from datetime import datetime

from pydantic import BaseModel, Field, HttpUrl


class Article(BaseModel):
    url: HttpUrl
    title: str
    published_at: datetime | None = None
    author: str | None = None
    summary: str | None = None

    content: str | None = None

    content_hash: str | None = None

    source: str = "Architectural Digest India"

    is_relevant: bool | None = None
    relevance_score: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )
    relevance_reason: str | None = None