from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.storage.base import Base
import app.storage.models  # noqa: F401

if TYPE_CHECKING:
    from app.storage.models.article import ArticleDB
    from app.storage.models.designer import DesignerDB
    from app.storage.models.rug import RugDB
    from app.storage.models.score import ScoreDB


class ProjectDB(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    article_id: Mapped[int] = mapped_column(
        ForeignKey("articles.id"),
        nullable=False,
    )

    designer_id: Mapped[int | None] = mapped_column(
        ForeignKey("designers.id"),
        nullable=True,
    )

    project_name: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    home_type: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    location: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    project_size: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    completion_year: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    homeowner_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    homeowner_profession: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    homeowner_industry: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    homeowner_city: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    homeowner_country: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    designer_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    designer_studio: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    designer_role: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    designer_city: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    designer_website: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )

    flooring: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    furniture: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    decor: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    textile_elements: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    sourcing_notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
    )

    article: Mapped["ArticleDB"] = relationship("ArticleDB", back_populates="projects")
    designer: Mapped["DesignerDB | None"] = relationship("DesignerDB", back_populates="projects")
    rugs: Mapped[list["RugDB"]] = relationship("RugDB", back_populates="project")
    scores: Mapped[list["ScoreDB"]] = relationship("ScoreDB", back_populates="project")