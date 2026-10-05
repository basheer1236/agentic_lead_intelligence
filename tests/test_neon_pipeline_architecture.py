import sys
import os
import unittest
from unittest.mock import patch, MagicMock

from fastapi.testclient import TestClient

from app.config.settings import settings
from app.storage.database import get_effective_database_url, get_engine, reset_db_engine
from app.ui.server import app
from app.ui.pipeline_runner import (
    runner,
    STATUS_IDLE,
    STATUS_RUNNING,
    STATUS_COMPLETED,
    STATUS_FAILED,
    STATUS_ABORTED,
)


class TestNeonCloudArchitecture(unittest.TestCase):
    """
    Verification suite for Neon PostgreSQL cloud migration and manual execution model.
    """

    def setUp(self):
        self.client = TestClient(app)

    def test_database_url_normalization_for_neon(self):
        """Verify Neon PostgreSQL URLs are normalized from postgres:// to postgresql:// while preserving query params."""
        neon_raw = "postgres://neondb_owner:npg_12345@ep-cool-fog-123.us-east-2.aws.neon.tech/neondb?sslmode=require"
        normalized = get_effective_database_url(neon_raw)
        self.assertTrue(normalized.startswith("postgresql://") or normalized.startswith("postgresql+pg8000://"))
        self.assertIn("ep-cool-fog-123.us-east-2.aws.neon.tech", normalized)
        self.assertIn("sslmode=require", normalized)

    def test_neon_pooled_connection_url(self):
        """Verify Neon pooled connections (PgBouncer) are handled properly."""
        neon_pooler = "postgresql://user:pass@ep-cool-fog-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require"
        normalized = get_effective_database_url(neon_pooler)
        self.assertTrue(normalized.startswith("postgresql://") or normalized.startswith("postgresql+pg8000://"))
        self.assertIn("ep-cool-fog-pooler", normalized)

    def test_cloud_engine_pooling_parameters(self):
        """Verify engine applies cloud connection resilience (pool_pre_ping and pool_recycle for Neon serverless)."""
        test_url = "postgresql://user:pass@ep-fake.neon.tech/neondb?sslmode=require"
        engine = get_engine(test_url)
        # Verify pool_pre_ping is enabled (essential for Neon scale-to-zero)
        self.assertTrue(engine.pool._pre_ping)
        # Verify recycle is configured to prevent stale dropped connections
        self.assertEqual(engine.pool._recycle, 300)

    def test_pipeline_not_started_on_application_startup(self):
        """CRITICAL: Verify pipeline is strictly IDLE on startup and does NOT execute automatically."""
        self.assertFalse(runner.is_running())
        snapshot = runner.get_snapshot()
        self.assertEqual(snapshot["status"], STATUS_IDLE)
        self.assertEqual(snapshot["current_stage"], 0)

    def test_page_load_does_not_trigger_pipeline(self):
        """CRITICAL: Verify accessing GET / (page load/refresh) serves HTML and does NOT trigger the pipeline."""
        initial_status = runner.get_snapshot()["status"]
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Agentic Lead Intelligence", response.text)
        self.assertIn("Trigger Pipeline Run", response.text)

        # Confirm pipeline did NOT start
        after_status = runner.get_snapshot()["status"]
        self.assertEqual(after_status, initial_status)
        self.assertFalse(runner.is_running())

    def test_pipeline_status_endpoint_returns_valid_lifecycle_state(self):
        """Verify GET /api/pipeline/status conforms to allowed lifecycle states."""
        response = self.client.get("/api/pipeline/status")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        valid_states = {STATUS_IDLE, STATUS_RUNNING, STATUS_COMPLETED, STATUS_FAILED, STATUS_ABORTED}
        self.assertIn(data["status"], valid_states)
        self.assertIn("progress_percent", data)
        self.assertIn("metrics", data)

    def test_pipeline_trigger_endpoint_propagates_batch_size(self):
        """Verify POST /api/pipeline/run accepts batch_size and starts execution only when clicked."""
        with patch.object(runner, "start", return_value=(True, "Pipeline execution started.")) as mock_start:
            response = self.client.post("/api/pipeline/run", json={"batch_size": 10, "single_test_mode": False})
            self.assertEqual(response.status_code, 200)
            mock_start.assert_called_once_with(batch_size=10, single_test_mode=False)

    def test_pipeline_abort_endpoint_triggers_cancellation(self):
        """Verify POST /api/pipeline/abort routes to cancellation mechanism."""
        with patch.object(runner, "cancel", return_value=(True, "Abort signal registered.")) as mock_cancel:
            response = self.client.post("/api/pipeline/abort")
            self.assertEqual(response.status_code, 200)
            mock_cancel.assert_called_once()

    def test_settings_rebinds_database_engine(self):
        """Verify updating database URL via POST /api/settings updates settings and rebinds engine."""
        test_url = "postgresql://neondb_owner:npg_test@ep-fake.neon.tech/neondb?sslmode=require"
        with patch("app.ui.server.reset_db_engine") as mock_reset, \
             patch("pathlib.Path.write_text") as mock_write:
            response = self.client.post("/api/settings", json={"database_url": test_url})
            self.assertEqual(response.status_code, 200)
            mock_reset.assert_called_once_with(test_url)


if __name__ == "__main__":
    unittest.main()
