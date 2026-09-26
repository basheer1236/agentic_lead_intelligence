from pydantic import BaseModel, HttpUrl


class Designer(BaseModel):
    name: str

    studio_name: str | None = None

    website: HttpUrl | None = None

    address: str | None = None
    city: str | None = None
    country: str | None = None

    email: str | None = None
    phone: str | None = None

    description: str | None = None

    linkedin_url: HttpUrl | None = None
    instagram_url: HttpUrl | None = None
    facebook_url: HttpUrl | None = None
    youtube_url: HttpUrl | None = None

    linkedin_verified: bool | None = False
    instagram_verified: bool | None = False
    linkedin_confidence: float | None = 0.0
    instagram_confidence: float | None = 0.0