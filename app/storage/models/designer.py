from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import DateTime, String, Text, Boolean, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.storage.base import Base

if TYPE_CHECKING:
    from app.storage.models.project import ProjectDB
    from app.storage.models.rug import RugDB


class DesignerDB(Base):
    __tablename__ = "designers"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    designer_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    studio_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    normalized_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    website: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True
    )

    address: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True
    )

    city: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    country: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    contact: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    email: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    company_description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    linkedin_url: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True
    )

    instagram_url: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True
    )

    facebook_url: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True
    )

    youtube_url: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True
    )

    linkedin_verified: Mapped[bool | None] = mapped_column(
        Boolean,
        nullable=True,
        default=False
    )

    instagram_verified: Mapped[bool | None] = mapped_column(
        Boolean,
        nullable=True,
        default=False
    )

    linkedin_confidence: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        default=0.0
    )

    instagram_confidence: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        default=0.0
    )

    last_enriched_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    projects: Mapped[list["ProjectDB"]] = relationship("ProjectDB", back_populates="designer")
    rugs: Mapped[list["RugDB"]] = relationship("RugDB", back_populates="designer")