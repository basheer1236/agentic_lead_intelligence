from pydantic import BaseModel


class Project(BaseModel):
    project_name: str | None = None
    project_type: str | None = None
    home_type: str | None = None

    location: str | None = None
    city: str | None = None
    state: str | None = None
    country: str | None = None

    size: str | None = None
    completion_year: int | None = None