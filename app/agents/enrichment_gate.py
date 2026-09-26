from typing import Literal


EnrichmentAction = Literal[
    "RUN_FULL_ENRICHMENT",
    "REFRESH_ENRICHMENT",
    "REUSE_EXISTING",
]


def decide_enrichment_action(
    freshness_status: str,
) -> EnrichmentAction:

    status = freshness_status.upper().strip()

    if status == "NEW":
        return "RUN_FULL_ENRICHMENT"

    if status == "STALE":
        return "REFRESH_ENRICHMENT"

    if status == "FRESH":
        return "REUSE_EXISTING"

    raise ValueError(
        f"Unsupported freshness status: {freshness_status}"
    )