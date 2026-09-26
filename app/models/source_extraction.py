from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator


class ExtractedField(BaseModel):
    field: str
    value: Optional[Any] = None
    source_url: str
    source_type: str
    evidence_text: Optional[str] = None
    confidence: float = Field(
        ge=0.0,
        le=1.0,
    )

    @field_validator("evidence_text", mode="before")
    @classmethod
    def normalize_evidence_text(cls, v: Any) -> Optional[str]:
        if isinstance(v, list):
            return " ".join(str(i) for i in v if i)
        return str(v) if v is not None else None


class SourceExtractionResult(BaseModel):
    source_url: str
    source_type: str
    fields: list[ExtractedField] = Field(
        default_factory=list
    )