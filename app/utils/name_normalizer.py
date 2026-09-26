import re
from typing import Optional


def normalize_designer_name(name: Optional[str]) -> Optional[str]:
    """
    Computes a deterministic canonical representation for designer / collaboration names.

    Rules:
    1. Lowercase and strip whitespace.
    2. Replace conjunctions ('and', '+') with '&'.
    3. Split multiple collaborator names separated by '&' or ','.
    4. Strip irrelevant punctuation from individual name tokens.
    5. Collapse multiple spaces.
    6. Deduplicate and sort collaborator names deterministically (alphabetically).
    7. Join sorted collaborator names with ' | '.

    Examples:
    - "Aayush Golecha & Kushaal Jhaveri" -> "aayush golecha | kushaal jhaveri"
    - "Aayush Golecha and Kushaal Jhaveri" -> "aayush golecha | kushaal jhaveri"
    - "Kushaal Jhaveri, Aayush Golecha" -> "aayush golecha | kushaal jhaveri"
    - "Aayush Golecha" -> "aayush golecha"
    """
    if not name or not isinstance(name, str):
        return None

    cleaned = name.strip().lower()
    if not cleaned:
        return None

    # Replace " and " or " + " with " & "
    cleaned = re.sub(r"\b(and|\+)\b", "&", cleaned, flags=re.IGNORECASE)

    # Split by "&", ",", or "|"
    raw_parts = re.split(r"[&,\|]", cleaned)

    parts = []
    for part in raw_parts:
        # Strip punctuation other than spaces
        p = re.sub(r"[^\w\s]", "", part).strip()
        # Collapse whitespace
        p = " ".join(p.split())
        if p:
            parts.append(p)

    if not parts:
        return None

    # Deduplicate and sort parts deterministically
    sorted_parts = sorted(list(dict.fromkeys(parts)))

    # Return canonical representation
    return " | ".join(sorted_parts)


def is_collaboration(name: Optional[str]) -> bool:
    """Returns True if the canonical representation contains multiple collaborators."""
    canonical = normalize_designer_name(name)
    if not canonical:
        return False
    return " | " in canonical
