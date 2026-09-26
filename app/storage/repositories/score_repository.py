from sqlalchemy import select
from sqlalchemy.orm import Session

from app.storage.models.score import ScoreDB


class ScoreRepository:

    @staticmethod
    def create(
        db: Session,
        project_id: int,
        lead_score: int | None = None,
        rug_opportunity_score: int | None = None,
    ) -> ScoreDB:

        score = ScoreDB(
            project_id=project_id,
            lead_score=lead_score,
            rug_opportunity_score=rug_opportunity_score,
        )

        db.add(score)
        db.commit()
        db.refresh(score)

        return score

    @staticmethod
    def get_by_id(
        db: Session,
        score_id: int
    ) -> ScoreDB | None:

        statement = select(ScoreDB).where(
            ScoreDB.id == score_id
        )

        return db.scalar(statement)

    @staticmethod
    def get_by_project_id(
        db: Session,
        project_id: int
    ) -> list[ScoreDB]:

        statement = select(ScoreDB).where(
            ScoreDB.project_id == project_id
        )

        return list(db.scalars(statement).all())