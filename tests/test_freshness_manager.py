from datetime import datetime, timedelta, timezone

from app.agents.freshness_manager import (
    get_freshness_status,
)


now = datetime.now(timezone.utc)


print(
    "No enrichment:",
    get_freshness_status(None),
)

print(
    "Recently enriched:",
    get_freshness_status(
        now - timedelta(days=5)
    ),
)

print(
    "Old enrichment:",
    get_freshness_status(
        now - timedelta(days=60)
    ),
)