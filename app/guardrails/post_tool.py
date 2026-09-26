"""
Post-tool guardrails for output validation, normalization, and telemetry update.
"""

from typing import Any
from app.errors import StateValidationError


def normalize_text_fields(data: Any) -> Any:
    """Recursively strip trailing whitespace and sanitize output strings."""
    if isinstance(data, str):
        return data.strip()
    elif isinstance(data, dict):
        return {k: normalize_text_fields(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [normalize_text_fields(item) for item in data]
    return data


def validate_tool_output(tool_name: str, output: Any) -> Any:
    """Validate and normalize tool output structure."""
    if output is None:
        return None

    normalized = normalize_text_fields(output)

    if tool_name in ("http_fetcher", "html_parser") and isinstance(normalized, dict):
        if "text" in normalized and not isinstance(normalized["text"], str):
            raise StateValidationError(f"Tool '{tool_name}' output field 'text' must be a string.")

    return normalized
