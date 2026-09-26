def calculate_lead_score(
    featured_in_ad: bool = False,
    luxury_residence: bool = False,
    rug_mentioned: bool = False,
    supplier_mentioned: bool = False,
    multiple_projects: bool = False,
    active_social: bool = False,
    contact_data: bool = False,
) -> int:

    score = 0

    if featured_in_ad:
        score += 20

    if luxury_residence:
        score += 20

    if rug_mentioned:
        score += 20

    if supplier_mentioned:
        score += 15

    if multiple_projects:
        score += 10

    if active_social:
        score += 10

    if contact_data:
        score += 5

    return min(score, 100)