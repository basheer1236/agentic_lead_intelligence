from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.storage.base import Base

if TYPE_CHECKING:
    from app.storage.models.designer import DesignerDB
    from app.storage.models.project import ProjectDB


class RugDB(Base):
    __tablename__ = "rugs"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id"),
        nullable=False
    )

    designer_id: Mapped[int | None] = mapped_column(
        ForeignKey("designers.id"),
        nullable=True
    )

    rug_used: Mapped[bool | None] = mapped_column(
        Boolean,
        nullable=True
    )

    rug_type: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    origin: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    material: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    supplier: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True
    )

    brand: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    handmade: Mapped[bool | None] = mapped_column(
        Boolean,
        nullable=True
    )

    handwoven: Mapped[bool | None] = mapped_column(
        Boolean,
        nullable=True
    )

    vintage: Mapped[bool | None] = mapped_column(
        Boolean,
        nullable=True
    )

    custom_made: Mapped[bool | None] = mapped_column(
        Boolean,
        nullable=True
    )

    imported: Mapped[bool | None] = mapped_column(
        Boolean,
        nullable=True
    )

    designer_custom_rug: Mapped[bool | None] = mapped_column(
        Boolean,
        nullable=True
    )

    matched_keywords: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    sourcing_notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    opportunity_score: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow
    )

    project: Mapped["ProjectDB"] = relationship("ProjectDB", back_populates="rugs")
    designer: Mapped["DesignerDB | None"] = relationship("DesignerDB", back_populates="rugs")