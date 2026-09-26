from app.storage.database import SessionLocal
from app.storage.repositories.rug_repository import RugRepository


def main():
    db = SessionLocal()

    try:
        rug = RugRepository.create(
            db=db,
            project_id=1,
            rug_used=True,
            rug_type="Persian",
            origin="India",
            material="Wool",
            supplier="Test Rug Supplier",
            brand="Test Rug Brand",
            handmade=True,
            handwoven=True,
            vintage=False,
            custom_made=False,
            imported=False,
            sourcing_notes="Sourced for the living room.",
            opportunity_score=70,
        )

        print("Rug created:")
        print("ID:", rug.id)
        print("Type:", rug.rug_type)
        print("Supplier:", rug.supplier)
        print("Opportunity Score:", rug.opportunity_score)

        found = RugRepository.get_by_id(
            db,
            rug.id
        )

        print("\nRug found by ID:")
        print("ID:", found.id if found else None)

        project_rugs = RugRepository.get_by_project_id(
            db,
            1
        )

        print("\nRugs for project:")
        print("Count:", len(project_rugs))

    finally:
        db.close()


if __name__ == "__main__":
    main()