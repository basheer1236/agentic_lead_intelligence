from sqlalchemy import select
from sqlalchemy.orm import Session

from app.storage.models.rug import RugDB


class RugRepository:

    @staticmethod
    def create(
        db: Session,
        project_id: int,
        designer_id: int | None = None,
        rug_used: bool | None = None,
        rug_type: str | None = None,
        origin: str | None = None,
        material: str | None = None,
        supplier: str | None = None,
        brand: str | None = None,
        handmade: bool | None = None,
        handwoven: bool | None = None,
        vintage: bool | None = None,
        custom_made: bool | None = None,
        imported: bool | None = None,
        designer_custom_rug: bool | None = None,
        matched_keywords: str | None = None,
        sourcing_notes: str | None = None,
        opportunity_score: int | None = None,
    ) -> RugDB:

        rug = RugDB(
            project_id=project_id,
            designer_id=designer_id,
            rug_used=rug_used,
            rug_type=rug_type,
            origin=origin,
            material=material,
            supplier=supplier,
            brand=brand,
            handmade=handmade,
            handwoven=handwoven,
            vintage=vintage,
            custom_made=custom_made,
            imported=imported,
            designer_custom_rug=designer_custom_rug,
            matched_keywords=matched_keywords,
            sourcing_notes=sourcing_notes,
            opportunity_score=opportunity_score,
        )

        db.add(rug)
        db.commit()
        db.refresh(rug)

        return rug

    @staticmethod
    def get_by_id(
        db: Session,
        rug_id: int
    ) -> RugDB | None:

        statement = select(RugDB).where(
            RugDB.id == rug_id
        )

        return db.scalar(statement)

    @staticmethod
    def get_by_project_id(
        db: Session,
        project_id: int
    ) -> list[RugDB]:

        statement = select(RugDB).where(
            RugDB.project_id == project_id
        )

        return list(db.scalars(statement).all())