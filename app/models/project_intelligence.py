from pydantic import BaseModel
from typing import Optional, List


class HomeownerInfo(BaseModel):
    name: Optional[str] = None
    profession: Optional[str] = None
    industry: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    public_profile_mentioned: str | bool | None = None


class DesignerInfo(BaseModel):
    name: Optional[str] = None
    studio: Optional[str] = None
    project_role: Optional[str] = None
    city: Optional[str] = None
    website: Optional[str] = None
    project_mention: str | bool | None = None


class ProjectIntelligence(BaseModel):
    project_name: Optional[str] = None
    home_type: Optional[str] = None
    location: Optional[str] = None
    project_size: Optional[str] = None
    completion_year: str | int | None = None

    homeowner: HomeownerInfo
    designer: DesignerInfo

    flooring: List[str] = []
    furniture: List[str] = []
    decor: List[str] = []
    textile_elements: List[str] = []
    sourcing_notes: List[str] = []