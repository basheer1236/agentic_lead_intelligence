from datetime import datetime

from pydantic import BaseModel, HttpUrl


class Evidence(BaseModel):
    entity: str
    field: str
    value: str

    source_url: HttpUrl

    evidence_text: str | None = None

    confidence: float

    retrieved_at: datetime