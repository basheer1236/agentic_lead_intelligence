from app.storage.database import SessionLocal
from app.storage.persistence.pipeline_persistence import (
    PipelinePersistenceService,
)


def main():
    db = SessionLocal()

    try:
        article, article_created = PipelinePersistenceService.save_article(
            db=db,
            url="https://example.com/test-pipeline-article",
            title="Pipeline Persistence Test Article",
            author="Test Author",
            summary="Testing complete pipeline persistence.",
            content_hash="pipeline-persistence-test-hash",
        )

        print("ARTICLE")
        print("ID:", article.id)
        print("Created:", article_created)

        project = PipelinePersistenceService.save_project(
            db=db,
            article_id=article.id,
            project_name="Pipeline Test Residence",
            home_type="Luxury Residence",
            location="Mumbai",
            project_size="5000 sq ft",
            completion_year=2026,
            homeowner_name="Test Homeowner",
            homeowner_profession="Entrepreneur",
            designer_name="Pipeline Test Designer",
            designer_studio="Pipeline Studio",
            designer_role="Interior Designer",
            designer_city="Mumbai",
            flooring="Marble",
            furniture="Custom furniture",
            decor="Contemporary decor",
            textile_elements="Handwoven rugs",
            sourcing_notes="Rug sourced from test supplier",
        )

        print("\nPROJECT")
        print("ID:", project.id)
        print("Name:", project.project_name)

        designer, designer_created = PipelinePersistenceService.save_designer(
            db=db,
            designer_name="Pipeline Test Designer",
            studio_name="Pipeline Studio",
            normalized_name="pipeline test designer",
            website="https://example.com/pipeline-designer",
            city="Mumbai",
            country="India",
            email="test@example.com",
        )

        print("\nDESIGNER")
        print("ID:", designer.id)
        print("Created:", designer_created)

        rug = PipelinePersistenceService.save_rug(
            db=db,
            project_id=project.id,
            rug_used=True,
            rug_type="Handwoven",
            origin="India",
            material="Wool",
            supplier="Test Rug Supplier",
            handmade=True,
            handwoven=True,
            custom_made=True,
            opportunity_score=100,
        )

        print("\nRUG")
        print("ID:", rug.id)
        print("Supplier:", rug.supplier)

        PipelinePersistenceService.save_scores(
            db=db,
            project_id=project.id,
            lead_score=100,
            rug_opportunity_score=100,
        )

        print("\nSCORES")
        print("Lead Score: 100")
        print("Rug Opportunity Score: 100")

        print("\n" + "=" * 50)
        print("PIPELINE PERSISTENCE TEST PASSED")
        print("=" * 50)

    finally:
        db.close()


if __name__ == "__main__":
    main()