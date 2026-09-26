def calculate_rug_opportunity_score(rug: dict) -> int:
    score = 0

    rug_used = rug.get("rug_used")

    rug_mentioned = (
        rug_used is True
        or str(rug_used).strip().lower() in ("yes", "true", "1")
    )

    if rug_mentioned:
        score += 30

    if rug.get("handmade") is True:
        score += 20

    if rug.get("custom_made") is True:
        score += 20

    if rug.get("luxury_project") is True:
        score += 15

    if rug.get("multiple_rugs") is True:
        score += 15

    return min(score, 100)