import re

import httpx
from bs4 import BeautifulSoup
from urllib.parse import urljoin


BASE_URL = "https://www.architecturaldigest.in"

EMAIL_PATTERN = re.compile(
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
)


def fetch_designer_profile(profile_url: str) -> dict:
    """
    Fetch publicly visible information from an AD PRO Directory
    designer profile.

    Deterministic extraction only.
    No guessing or LLM inference.
    """

    if not profile_url:
        raise ValueError("Profile URL cannot be empty")

    if "/adpro/directory/profile/" not in profile_url:
        raise ValueError(
            "URL is not an AD PRO Directory profile"
        )

    response = httpx.get(
        profile_url,
        timeout=20,
        follow_redirects=True,
        headers={
            "User-Agent": "Mozilla/5.0"
        },
    )

    response.raise_for_status()

    soup = BeautifulSoup(
        response.text,
        "lxml",
    )

    # =========================================================
    # Remove scripts / styles / navigation
    # =========================================================

    for tag in soup(
        [
            "script",
            "style",
            "noscript",
            "nav",
            "footer",
        ]
    ):
        tag.decompose()

    # =========================================================
    # TITLE
    # =========================================================

    title = None

    if soup.title:
        title = soup.title.get_text(
            " ",
            strip=True,
        )

    # =========================================================
    # VISIBLE TEXT
    # =========================================================

    text = soup.get_text(
        " ",
        strip=True,
    )

    # =========================================================
    # LINKS
    # =========================================================

    links = []
    seen_urls = set()

    for link in soup.find_all(
        "a",
        href=True,
    ):
        link_text = link.get_text(
            " ",
            strip=True,
        )

        href = str(
            link.get("href")
        ).strip()

        if not href:
            continue

        full_url = urljoin(
            BASE_URL,
            href,
        )

        # Ignore affiliate/tracking links.
        if "cna.st" in full_url.lower():
            continue

        if full_url in seen_urls:
            continue

        seen_urls.add(
            full_url
        )

        links.append(
            {
                "text": link_text,
                "url": full_url,
            }
        )

    # =========================================================
    # EMAILS
    # =========================================================

    emails = set()

    # Only inspect links that explicitly represent email.
    for link in soup.find_all(
        "a",
        href=True,
    ):
        href = str(
            link.get("href")
        ).strip()

        if not href.lower().startswith(
            "mailto:"
        ):
            continue

        email_value = href[
            len("mailto:")
        ].strip()

        # Remove query parameters.
        email_value = email_value.split(
            "?",
            1,
        )[0].strip()

        match = EMAIL_PATTERN.fullmatch(
            email_value
        )

        if match:
            emails.add(
                email_value
            )

    # Also inspect visible text, but only after removing
    # scripts/styles/navigation/footer.
    visible_emails = EMAIL_PATTERN.findall(
        text
    )

    for email in visible_emails:
        emails.add(
            email.strip()
        )

    emails = sorted(
        emails
    )

    # =========================================================
    # PHONES
    # =========================================================

    phones = set()

    for link in soup.find_all(
        "a",
        href=True,
    ):
        href = str(
            link.get("href")
        ).strip()

        if href.lower().startswith(
            "tel:"
        ):
            phone = href[
                len("tel:")
            ].strip()

            if phone:
                phones.add(
                    phone
                )

    phones = sorted(
        phones
    )

    # =========================================================
    # SOCIAL LINKS
    # =========================================================

    social = {
        "linkedin": [],
        "instagram": [],
        "facebook": [],
        "youtube": [],
    }

    for link in links:

        url = link["url"]
        lower_url = url.lower()

        if "linkedin.com" in lower_url:

            if url not in social["linkedin"]:
                social["linkedin"].append(
                    url
                )

        elif "instagram.com" in lower_url:

            if url not in social["instagram"]:
                social["instagram"].append(
                    url
                )

        elif "facebook.com" in lower_url:

            if url not in social["facebook"]:
                social["facebook"].append(
                    url
                )

        elif "youtube.com" in lower_url:

            if url not in social["youtube"]:
                social["youtube"].append(
                    url
                )

    # =========================================================
    # WEBSITE
    # =========================================================

    websites = []

    ignored_domains = [
        "architecturaldigest.in",
        "linkedin.com",
        "instagram.com",
        "facebook.com",
        "youtube.com",
    ]

    for link in links:

        url = link["url"]
        lower_url = url.lower()

        if any(
            domain in lower_url
            for domain in ignored_domains
        ):
            continue

        if (
            url.startswith("http://")
            or url.startswith("https://")
        ):
            if url not in websites:
                websites.append(
                    url
                )

    # =========================================================
    # RETURN
    # =========================================================

    return {
        "profile_url": profile_url,
        "title": title,
        "text": text,
        "links": links,
        "websites": websites,
        "emails": emails,
        "phones": phones,
        "social": social,
    }