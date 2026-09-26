from datetime import datetime, timedelta, timezone


def get_freshness_status(
    last_enriched_at: datetime | None,
    fresh_days: int = 30,
) -> str:
    """
    Return NEW, FRESH, or STALE based on enrichment age.
    """

    if last_enriched_at is None:
        return "NEW"

    if last_enriched_at.tzinfo is None:
        last_enriched_at = last_enriched_at.replace(
            tzinfo=timezone.utc
        )

    now = datetime.now(timezone.utc)

    freshness_deadline = (
        now - timedelta(days=fresh_days)
    )

    if last_enriched_at >= freshness_deadline:
        return "FRESH"

    return "STALE"