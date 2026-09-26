from app.storage.database import SessionLocal

from app.storage.repositories.article_repository import ArticleRepository
from app.storage.repositories.project_repository import ProjectRepository
from app.storage.repositories.designer_repository import DesignerRepository
from app.storage.repositories.source_repository import SourceRepository
from app.storage.repositories.rug_repository import RugRepository
from app.storage.repositories.score_repository import ScoreRepository


def main():
    db = SessionLocal()

    try:
        # --------------------------------------------------
        # 1. ARTICLE
        # --------------------------------------------------
        article, created = ArticleRepository.get_or_create(
            db=db,
            url="https://example.com/e2e-test",
            title="E2E Residential Project",
            author="Test Author",
            summary="End-to-end database test",
            content_hash="e2e_hash_001",
        )

        print("ARTICLE")
        print("ID:", article.id)
        print("Created:", created)

        # --------------------------------------------------
        # 2. PROJECT
        # --------------------------------------------------
        project = ProjectRepository.create(
            db=db,
            article_id=article.id,
            project_name="E2E Mumbai Residence",
            home_type="Apartment",
            location="Mumbai",
            designer_name="E2E Designer",
            designer_studio="E2E Studio",
        )

        print("\nPROJECT")
        print("ID:", project.id)
        print("Name:", project.project_name)

        # --------------------------------------------------
        # 3. DESIGNER
        # --------------------------------------------------
        designer = DesignerRepository.create(
            db=db,
            designer_name="E2E Designer",
            studio_name="E2E Studio",
            normalized_name="e2e designer",
            website="https://example.com/e2e-studio",
            city="Mumbai",
            country="India",
            email="designer@example.com",
        )

        print("\nDESIGNER")
        print("ID:", designer.id)
        print("Name:", designer.designer_name)

        # --------------------------------------------------
        # 4. EVIDENCE / SOURCE
        # --------------------------------------------------
        source = SourceRepository.create(
            db=db,
            designer_id=designer.id,
            source_url="https://example.com/e2e-studio",
            source_type="official_website",
            field="email",
            value="designer@example.com",
            evidence_text="Contact information found on official website.",
            confidence=0.95,
        )

        print("\nSOURCE / EVIDENCE")
        print("ID:", source.id)
        print("Field:", source.field)
        print("Confidence:", source.confidence)

        # --------------------------------------------------
        # 5. RUG
        # --------------------------------------------------
        rug = RugRepository.create(
            db=db,
            project_id=project.id,
            rug_used=True,
            rug_type="Handwoven",
            origin="India",
            material="Wool",
            supplier="E2E Rug Supplier",
            handmade=True,
            handwoven=True,
            custom_made=True,
            opportunity_score=100,
        )

        print("\nRUG")
        print("ID:", rug.id)
        print("Supplier:", rug.supplier)
        print("Opportunity Score:", rug.opportunity_score)

        # --------------------------------------------------
        # 6. SCORES
        # --------------------------------------------------
        score = ScoreRepository.create(
            db=db,
            project_id=project.id,
            lead_score=100,
            rug_opportunity_score=100,
        )

        print("\nSCORES")
        print("ID:", score.id)
        print("Lead Score:", score.lead_score)
        print(
            "Rug Opportunity Score:",
            score.rug_opportunity_score,
        )

        # --------------------------------------------------
        # FINAL
        # --------------------------------------------------
        print("\n" + "=" * 50)
        print("END-TO-END DATABASE TEST PASSED")
        print("=" * 50)

    finally:
        db.close()


if __name__ == "__main__":
    main()