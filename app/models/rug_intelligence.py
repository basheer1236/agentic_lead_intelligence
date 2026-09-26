from typing import Optional
from pydantic import BaseModel


class RugIntelligence(BaseModel):
    rug_used: Optional[str] = "Unclear"  # Yes / No / Unclear
    rug_type: Optional[str] = None
    rug_origin: Optional[str] = None
    rug_material: Optional[str] = None
    rug_supplier: Optional[str] = None
    rug_brand: Optional[str] = None

    handmade: Optional[bool] = None
    handwoven: Optional[bool] = None
    vintage: Optional[bool] = None
    custom_made: Optional[bool] = None
    imported: Optional[bool] = None
    multiple_rugs: bool | None = None
    luxury_project: bool | None = None
    designer_custom_rug: bool | None = None  # True if designed/customized by interior designer
    matched_keywords: Optional[str] = None   # Floor covering keywords: rug, carpet, runner, etc.

    room_location: Optional[str] = None
    rug_notes: Optional[str] = None
    opportunity_score: int = 0