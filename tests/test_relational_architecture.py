import sys
from pathlib import Path
import pandas as pd

from app.storage.database import SessionLocal
from app.storage.models.project import ProjectDB
from app.storage.models.designer import DesignerDB
from app.storage.models.rug import RugDB
from app.storage.models.article import ArticleDB
from app.storage.models.score import ScoreDB
from app.storage.persistence.pipeline_persistence import PipelinePersistenceService
from app.export.excel_exporter import ExcelExporter


def test_models_have_foreign_keys():
    """Verify ProjectDB and RugDB have designer_id foreign key attributes."""
    assert hasattr(ProjectDB, "designer_id")
    assert hasattr(RugDB, "designer_id")
    assert hasattr(RugDB, "project_id")
    print("test_models_have_foreign_keys PASSED")


def test_sqlalchemy_relationships_resolve():
    """Verify SQLAlchemy relationships resolve between Article, Project, Designer, and Rug."""
    db = SessionLocal()
    try:
        article, _ = PipelinePersistenceService.save_article(
            db=db,
            url="https://example.com/test-relational-art-2",
            title="Test Relational Article 2",
        )

        designer, _ = PipelinePersistenceService.save_designer(
            db=db,
            designer_name="Relational Test Designer 2",
            studio_name="Relational Studio 2",
            normalized_name="relational test designer 2",
            website="https://example.com/relational-designer-2",
        )

        project = PipelinePersistenceService.save_project(
            db=db,
            article_id=article.id,
            designer_id=designer.id,
            project_name="Relational Test House 2",
        )

        rug = PipelinePersistenceService.save_rug(
            db=db,
            project_id=project.id,
            designer_id=designer.id,
            rug_used="Yes",
            rug_type="Kilim",
        )

        db.refresh(project)
        db.refresh(rug)

        assert project.designer_id == designer.id
        assert project.designer.id == designer.id
        assert rug.project_id == project.id
        assert rug.designer_id == designer.id
        assert rug.project.id == project.id
        assert rug.designer.id == designer.id
        print("test_sqlalchemy_relationships_resolve PASSED")

    finally:
        db.close()


def test_idempotent_designer_persistence():
    """Verify repeated pipeline execution does not duplicate designers."""
    db = SessionLocal()
    try:
        designer_1, created_1 = PipelinePersistenceService.save_designer(
            db=db,
            designer_name="Idempotent Test Designer 2",
            normalized_name="idempotent test designer 2",
            website="https://example.com/idempotent-designer-2",
        )

        designer_2, created_2 = PipelinePersistenceService.save_designer(
            db=db,
            designer_name="Idempotent Test Designer 2",
            normalized_name="idempotent test designer 2",
            website="https://example.com/idempotent-designer-2",
        )

        assert designer_1.id == designer_2.id
        assert created_2 is False
        print("test_idempotent_designer_persistence PASSED")

    finally:
        db.close()


def test_excel_export_relational_structure():
    """Verify Excel output contains 4 sheets, README, required IDs, and valid FK joins."""
    db = SessionLocal()
    try:
        exporter = ExcelExporter()
        out_path = exporter.export(db, filename="test_relational_export.xlsx", exclude_test_data=False)
        assert out_path.exists()

        xls = pd.ExcelFile(out_path)
        sheet_names = xls.sheet_names

        assert sheet_names == [
            "README",
            "Lead Intelligence Master",
            "Interior Designer Master",
            "Rug Opportunity Tracker",
        ]

        readme_df = pd.read_excel(xls, sheet_name="README")
        lead_df = pd.read_excel(xls, sheet_name="Lead Intelligence Master")
        designer_df = pd.read_excel(xls, sheet_name="Interior Designer Master")
        rug_df = pd.read_excel(xls, sheet_name="Rug Opportunity Tracker")

        readme_text = " ".join(str(val) for val in readme_df.fillna("").values.flatten())
        assert "WORKBOOK PURPOSE" in readme_text
        assert "designer_id" in readme_text
        assert "project_id" in readme_text

        assert "project_id" in lead_df.columns
        assert "designer_id" in lead_df.columns
        assert "article_id" in lead_df.columns

        assert "designer_id" in designer_df.columns

        assert "rug_id" in rug_df.columns
        assert "project_id" in rug_df.columns
        assert "designer_id" in rug_df.columns

        designer_ids = set(designer_df["designer_id"].dropna().astype(int))
        lead_project_ids = set(lead_df["project_id"].dropna().astype(int))
        lead_designer_ids = set(lead_df["designer_id"].dropna().astype(int))

        for d_id in lead_designer_ids:
            assert d_id in designer_ids, f"Lead designer_id {d_id} not found in Interior Designer Master"

        rug_project_ids = set(rug_df["project_id"].dropna().astype(int))
        for p_id in rug_project_ids:
            assert p_id in lead_project_ids, f"Rug project_id {p_id} not found in Lead Intelligence Master"

        rug_designer_ids = set(rug_df["designer_id"].dropna().astype(int))
        for d_id in rug_designer_ids:
            assert d_id in designer_ids, f"Rug designer_id {d_id} not found in Interior Designer Master"

        print("test_excel_export_relational_structure PASSED")

    finally:
        db.close()


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    test_models_have_foreign_keys()
    test_sqlalchemy_relationships_resolve()
    test_idempotent_designer_persistence()
    test_excel_export_relational_structure()
    print("ALL RELATIONAL ARCHITECTURE TESTS PASSED SUCCESSFULLY!")
