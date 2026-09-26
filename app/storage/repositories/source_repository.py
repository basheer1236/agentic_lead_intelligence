from sqlalchemy import select
from sqlalchemy.orm import Session

from app.storage.models.source import SourceDB


class SourceRepository:

    @staticmethod
    def create(
        db: Session,
        source_url: str,
        source_type: str,
        field: str,
        value: str | None = None,
        evidence_text: str | None = None,
        confidence: float | None = None,
        designer_id: int | None = None,
    ) -> SourceDB:

        source = SourceDB(
            designer_id=designer_id,
            source_url=source_url,
            source_type=source_type,
            field=field,
            value=value,
            evidence_text=evidence_text,
            confidence=confidence,
        )

        db.add(source)
        db.commit()
        db.refresh(source)

        return source

    @staticmethod
    def get_existing(
        db: Session,
        designer_id: int,
        field: str,
        value: str | None,
        source_url: str,
    ) -> SourceDB | None:

        statement = select(SourceDB).where(
            SourceDB.designer_id == designer_id,
            SourceDB.field == field,
            SourceDB.value == value,
            SourceDB.source_url == source_url,
        )

        return db.scalar(statement)
    def get_by_id(
        db: Session,
        source_id: int
    ) -> SourceDB | None:

        statement = select(SourceDB).where(
            SourceDB.id == source_id
        )

        return db.scalar(statement)

    @staticmethod
    def get_by_designer_id(
        db: Session,
        designer_id: int
    ) -> list[SourceDB]:

        statement = select(SourceDB).where(
            SourceDB.designer_id == designer_id
        )

        return list(db.scalars(statement).all())

    @staticmethod
    def get_by_field(
        db: Session,
        designer_id: int,
        field: str
    ) -> list[SourceDB]:

        statement = select(SourceDB).where(
            SourceDB.designer_id == designer_id,
            SourceDB.field == field,
        )

        return list(db.scalars(statement).all())