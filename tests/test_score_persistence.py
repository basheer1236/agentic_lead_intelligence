from app.storage.database import SessionLocal
from app.storage.persistence.score_persistence import (
    ScorePersistenceService,
)


def main():
    db = SessionLocal()

    try:
        score = ScorePersistenceService.save_scores(
            db=db,
            project_id=1,
            lead_score=100,
            rug_opportunity_score=100,
        )

        print("Scores persisted successfully:")
        print("Score ID:", score.id)
        print("Lead Score:", score.lead_score)
        print(
            "Rug Opportunity Score:",
            score.rug_opportunity_score,
        )

    finally:
        db.close()


if __name__ == "__main__":
    main()