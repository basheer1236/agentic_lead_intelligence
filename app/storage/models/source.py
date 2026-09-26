from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.storage.base import Base


class SourceDB(Base):
    __tablename__ = "sources"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    designer_id: Mapped[int | None] = mapped_column(
        ForeignKey("designers.id"),
        nullable=True
    )

    source_url: Mapped[str] = mapped_column(
        String(1000),
        nullable=False
    )

    source_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    field: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    value: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    evidence_text: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    confidence: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )

    retrieved_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow
    )