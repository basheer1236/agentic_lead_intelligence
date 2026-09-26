INTERIOR_DESIGN_KEYWORDS = [
    "home",
    "house",
    "residence",
    "villa",
    "apartment",
    "penthouse",
    "bungalow",
    "mansion",
    "renovation",
    "refurbishment",
    "restoration",
    "interior design",
    "interior",
    "interiors",
    "residential",
    "restaurant",
    "cafe",
    "hotel",
    "office",
    "commercial",
    "space",
    "retreat",
    "bar",
    "boutique",
    "studio",
    "hospitality",
    "store",
    "dining",
    "lounge",
]

EXCLUDED_KEYWORDS = [
    "product review",
    "furniture review",
    "fashion",
    "event",
    "awards",
]


def is_potential_interior_design_article(title: str, summary: str = "") -> bool:
    text = f"{title} {summary}".lower()

    has_keyword = any(
        keyword in text
        for keyword in INTERIOR_DESIGN_KEYWORDS
    )

    has_excluded = any(
        keyword in text
        for keyword in EXCLUDED_KEYWORDS
    )

    return has_keyword and not has_excluded


def filter_articles(articles: list[dict]) -> list[dict]:
    return [
        article
        for article in articles
        if is_potential_interior_design_article(
            article.get("title", ""),
            article.get("summary", ""),
        )
    ]