from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.storage.base import Base

if TYPE_CHECKING:
    from app.storage.models.project import ProjectDB


class ScoreDB(Base):
    __tablename__ = "scores"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id"),
        nullable=False
    )

    lead_score: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    rug_opportunity_score: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    scored_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow
    )

    project: Mapped["ProjectDB"] = relationship("ProjectDB", back_populates="scores")