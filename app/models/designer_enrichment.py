from typing import Optional, List

from pydantic import BaseModel, Field


class KeyPerson(BaseModel):
    name: Optional[str] = None
    title: Optional[str] = None
    role: Optional[str] = None
    linkedin_url: Optional[str] = None


class Evidence(BaseModel):
    field: str
    value: Optional[str] = None
    source_url: Optional[str] = None
    source_type: Optional[str] = None
    evidence_text: Optional[str] = None
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)


class DesignerEnrichment(BaseModel):
    designer_name: Optional[str] = None
    studio_name: Optional[str] = None

    website: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None

    contact: Optional[str] = None
    email: Optional[str] = None

    company_description: Optional[str] = None

    key_people: List[KeyPerson] = Field(default_factory=list)

    linkedin_url: Optional[str] = None
    instagram_url: Optional[str] = None
    facebook_url: Optional[str] = None
    youtube_url: Optional[str] = None

    linkedin_verified: bool = False
    instagram_verified: bool = False
    linkedin_confidence: float = 0.0
    instagram_confidence: float = 0.0

    evidence: List[Evidence] = Field(default_factory=list)