from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.storage.base import Base

if TYPE_CHECKING:
    from app.storage.models.project import ProjectDB


class ArticleDB(Base):
    __tablename__ = "articles"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    url: Mapped[str] = mapped_column(
        String(1000),
        unique=True,
        nullable=False,
    )

    title: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    author: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    summary: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    content_hash: Mapped[str | None] = mapped_column(
        String(64),
        unique=True,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
    )

    projects: Mapped[list["ProjectDB"]] = relationship("ProjectDB", back_populates="article")