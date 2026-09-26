"""
Structured logging and telemetry module for Agentic Lead Intelligence.
"""

import json
import logging
import sys
import time
from datetime import datetime, timezone
from typing import Any


logger = logging.getLogger("lead_intelligence")
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter("[%(asctime)s] %(levelname)s [%(name)s] %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)


SENSITIVE_KEYS = {"api_key", "password", "secret", "token", "authorization"}


def _sanitize_dict(data: dict[str, Any]) -> dict[str, Any]:
    """Remove sensitive keys from telemetry payloads."""
    clean = {}
    for key, value in data.items():
        if any(s in key.lower() for s in SENSITIVE_KEYS):
            clean[key] = "***REDACTED***"
        elif isinstance(value, dict):
            clean[key] = _sanitize_dict(value)
        else:
            clean[key] = value
    return clean


def log_telemetry(event: str, **kwargs: Any) -> dict[str, Any]:
    """
    Log a structured JSON telemetry event.
    """
    payload = {
        "event": event,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        **_sanitize_dict(kwargs),
    }
    logger.info(json.dumps(payload))
    return payload


class ExecutionTimer:
    """Context manager for tracking node/tool duration."""

    def __init__(self, name: str):
        self.name = name
        self.start_time = 0.0
        self.duration = 0.0

    def __enter__(self):
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.duration = round(time.perf_counter() - self.start_time, 4)
