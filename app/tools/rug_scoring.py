def calculate_rug_opportunity_score(rug: dict) -> int:
    score = 0

    if rug.get("rug_used") == "Yes":
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