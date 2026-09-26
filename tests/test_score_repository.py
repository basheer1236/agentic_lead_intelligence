from app.storage.database import SessionLocal
from app.storage.repositories.score_repository import ScoreRepository


def main():
    db = SessionLocal()

    try:
        score = ScoreRepository.create(
            db=db,
            project_id=1,
            lead_score=100,
            rug_opportunity_score=70,
        )

        print("Score created:")
        print("ID:", score.id)
        print("Lead Score:", score.lead_score)
        print("Rug Opportunity Score:", score.rug_opportunity_score)

        found = ScoreRepository.get_by_id(
            db,
            score.id
        )

        print("\nScore found by ID:")
        print("ID:", found.id if found else None)

        project_scores = ScoreRepository.get_by_project_id(
            db,
            1
        )

        print("\nScores for project:")
        print("Count:", len(project_scores))

    finally:
        db.close()


if __name__ == "__main__":
    main()