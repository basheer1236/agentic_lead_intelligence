import pytest
import pandas as pd
from sqlalchemy import text
from app.utils.name_normalizer import normalize_designer_name, is_collaboration
from app.storage.database import SessionLocal
from app.storage.repositories.designer_repository import DesignerRepository
from app.storage.persistence.pipeline_persistence import PipelinePersistenceService
from app.export.excel_exporter import ExcelExporter


def test_scenario_1_same_individual_name():
    norm1 = normalize_designer_name("Kumpal Vaid")
    norm2 = normalize_designer_name("kumpal vaid  ")
    assert norm1 == "kumpal vaid"
    assert norm2 == "kumpal vaid"
    assert is_collaboration(norm1) is False


def test_scenario_2_conjunction_variants():
    norm1 = normalize_designer_name("Aayush Golecha & Kushaal Jhaveri")
    norm2 = normalize_designer_name("Aayush Golecha and Kushaal Jhaveri")
    norm3 = normalize_designer_name("Aayush Golecha, Kushaal Jhaveri")
    assert norm1 == "aayush golecha | kushaal jhaveri"
    assert norm2 == "aayush golecha | kushaal jhaveri"
    assert norm3 == "aayush golecha | kushaal jhaveri"
    assert is_collaboration(norm1) is True


def test_scenario_3_reversed_collaborator_order():
    norm_forward = normalize_designer_name("Aayush Golecha & Kushaal Jhaveri")
    norm_reversed = normalize_designer_name("Kushaal Jhaveri & Aayush Golecha")
    assert norm_forward == norm_reversed
    assert norm_forward == "aayush golecha | kushaal jhaveri"


def test_scenario_4_individual_vs_collaboration_distinctness():
    norm_individual = normalize_designer_name("Aayush Golecha")
    norm_collab = normalize_designer_name("Aayush Golecha & Kushaal Jhaveri")
    assert norm_individual == "aayush golecha"
    assert norm_collab == "aayush golecha | kushaal jhaveri"
    assert norm_individual != norm_collab


def test_scenario_5_and_6_studio_aware_persistence():
    session = SessionLocal()
    try:
        # Same collaboration + same studio -> same designer_id
        d1, _ = PipelinePersistenceService.save_designer(
            db=session,
            designer_name="Test Partner A & Test Partner B",
            studio_name="UnitTest Studio XYZ"
        )
        d2, created2 = PipelinePersistenceService.save_designer(
            db=session,
            designer_name="Test Partner A and Test Partner B",
            studio_name="UnitTest Studio XYZ"
        )
        assert created2 is False
        assert d1.id == d2.id

        # Same studio + different individual -> different designer_id
        d3, created3 = PipelinePersistenceService.save_designer(
            db=session,
            designer_name="Test Partner A",
            studio_name="UnitTest Studio XYZ"
        )
        assert d3.id != d1.id
    finally:
        session.close()


def test_scenario_7_fuzzy_only_similarity_does_not_merge():
    session = SessionLocal()
    try:
        d1, _ = PipelinePersistenceService.save_designer(
            db=session,
            designer_name="The Comma Collective Design Practice",
            studio_name="Studio Alpha"
        )
        d2, created2 = PipelinePersistenceService.save_designer(
            db=session,
            designer_name="The Comma Collective Architecture Firm",
            studio_name="Studio Alpha"
        )
        # Distinct names should not automatically merge based on fuzzy tokens alone
        assert d1.id != d2.id
    finally:
        session.close()


def test_scenarios_8_to_13_database_foreign_keys_and_migration_integrity():
    session = SessionLocal()
    try:
        # ID 25 preserved as individual
        d25 = session.execute(text("SELECT id, designer_name, normalized_name FROM designers WHERE id = 25")).mappings().first()
        assert d25 is not None
        assert d25["designer_name"] == "Aayush Golecha"
        assert d25["normalized_name"] == "aayush golecha"

        # IDs 4, 5, 41 resolved to canonical ID 4
        d4 = session.execute(text("SELECT id, designer_name, normalized_name FROM designers WHERE id = 4")).mappings().first()
        assert d4 is not None
        assert d4["normalized_name"] == "aayush golecha | kushaal jhaveri"

        d5 = session.execute(text("SELECT id FROM designers WHERE id = 5")).first()
        d41 = session.execute(text("SELECT id FROM designers WHERE id = 41")).first()
        assert d5 is None
        assert d41 is None

        # Check for orphaned projects and rugs
        orphaned_p = session.execute(text("SELECT COUNT(*) FROM projects WHERE designer_id IS NOT NULL AND designer_id NOT IN (SELECT id FROM designers)")).scalar()
        orphaned_r = session.execute(text("SELECT COUNT(*) FROM rugs WHERE designer_id IS NOT NULL AND designer_id NOT IN (SELECT id FROM designers)")).scalar()
        assert orphaned_p == 0
        assert orphaned_r == 0

        # Existing projects/rugs retain valid designer_id
        p7 = session.execute(text("SELECT designer_id FROM projects WHERE id = 7")).scalar()
        p8 = session.execute(text("SELECT designer_id FROM projects WHERE id = 8")).scalar()
        assert p7 == 4
        assert p8 == 25
    finally:
        session.close()


def test_scenario_14_excel_designer_master_no_duplicates():
    session = SessionLocal()
    try:
        exporter = ExcelExporter()
        path = exporter.export(session)
        df = pd.read_excel(path, sheet_name="Interior Designer Master")

        golecha_rows = df[df["designer_name"].str.contains("Golecha", na=False)]
        assert len(golecha_rows) == 2  # Exactly 1 for Aayush Golecha and 1 for Aayush Golecha & Kushaal Jhaveri

        names = set(golecha_rows["designer_name"].tolist())
        assert "Aayush Golecha" in names
        assert "Aayush Golecha & Kushaal Jhaveri" in names
        assert "Aayush Golecha, Kushaal Jhaveri" not in names
        assert "Aayush Golecha and Kushaal Jhaveri" not in names
    finally:
        session.close()
