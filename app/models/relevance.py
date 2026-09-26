from pydantic import BaseModel, Field


class RelevanceResult(BaseModel):
    is_relevant: bool
    confidence: float = Field(ge=0, le=1)
    article_type: str | None = None
    reason: str | None = None