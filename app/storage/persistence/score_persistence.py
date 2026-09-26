from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.storage.repositories.score_repository import ScoreRepository


class ScorePersistenceService:

    @staticmethod
    def save_scores(
        db: Session,
        project_id: int,
        lead_score: int | None,
        rug_opportunity_score: int | None,
    ):
        existing_list = ScoreRepository.get_by_project_id(
            db=db, project_id=project_id
        )

        if existing_list:
            score = existing_list[0]
            if lead_score is not None:
                score.lead_score = lead_score
            if rug_opportunity_score is not None:
                score.rug_opportunity_score = rug_opportunity_score
            score.scored_at = datetime.now(timezone.utc)
            db.commit()
            db.refresh(score)
            return score

        return ScoreRepository.create(
            db=db,
            project_id=project_id,
            lead_score=lead_score,
            rug_opportunity_score=rug_opportunity_score,
        )