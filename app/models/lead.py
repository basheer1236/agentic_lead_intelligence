from pydantic import BaseModel, Field


class LeadScore(BaseModel):
    featured_in_ad: int = 0
    luxury_residence: int = 0
    rug_mentioned: int = 0
    supplier_mentioned: int = 0
    multiple_projects: int = 0
    active_social: int = 0
    contact_data: int = 0

    total: int = Field(
        default=0,
        ge=0,
        le=100,
    )