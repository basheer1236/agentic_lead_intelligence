from urllib.parse import urlparse


def _normalize_domain(domain: str) -> str:
    return domain.lower().replace("www.", "").strip()


def classify_source(url: str, official_domain: str | None = None) -> str:
    hostname = _normalize_domain(urlparse(url).netloc)

    if hostname.endswith("architecturaldigest.in"):
        return "architectural_digest"

    if hostname.endswith("linkedin.com"):
        return "linkedin"

    if hostname.endswith("instagram.com"):
        return "instagram"

    if hostname.endswith("facebook.com"):
        return "facebook"

    if hostname.endswith("youtube.com"):
        return "youtube"

    if official_domain:
        normalized_official = _normalize_domain(official_domain)

        if (
            hostname == normalized_official
            or hostname.endswith("." + normalized_official)
        ):
            return "official_website"

    return "public_web"