from pydantic import BaseModel, Field


class RugMention(BaseModel):
    used: bool = False

    rug_type: str | None = None
    style: str | None = None
    origin: str | None = None
    material: str | None = None

    supplier: str | None = None
    brand: str | None = None

    handmade: bool | None = None
    handwoven: bool | None = None
    custom_made: bool | None = None
    vintage: bool | None = None
    imported: bool | None = None

    room_location: str | None = None

    notes: str | None = None

    opportunity_score: int = Field(
        default=0,
        ge=0,
        le=100,
    )