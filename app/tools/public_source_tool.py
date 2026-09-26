from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup

from app.tools.website_tool import _fetch_with_playwright
from app.utils.source_classifier import classify_source


USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 "
    "(KHTML, like Gecko) "
    "Chrome/131.0.0.0 Safari/537.36"
)


def _extract_emails(text: str) -> list[str]:
    import re

    pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"

    return sorted(set(re.findall(pattern, text)))


def _extract_phones(text: str) -> list[str]:
    import re

    pattern = r"""
        (?:
            \+?\d{1,3}[\s.-]?
        )?
        (?:\(?\d{2,5}\)?[\s.-]?)
        \d{3,4}[\s.-]?\d{3,4}
    """

    matches = re.findall(
        pattern,
        text,
        flags=re.VERBOSE,
    )

    return sorted(
        set(
            match.strip()
            for match in matches
            if len(match.strip()) >= 7
        )
    )


def _extract_social_links(
    soup: BeautifulSoup,
    base_url: str,
) -> dict:

    social = {
        "linkedin": [],
        "instagram": [],
        "facebook": [],
        "youtube": [],
    }

    for link in soup.find_all(
        "a",
        href=True,
    ):

        href = urljoin(
            base_url,
            link["href"],
        )

        hostname = urlparse(
            href
        ).netloc.lower()

        if "linkedin.com" in hostname:
            social["linkedin"].append(href)

        elif "instagram.com" in hostname:
            social["instagram"].append(href)

        elif "facebook.com" in hostname:
            social["facebook"].append(href)

        elif "youtube.com" in hostname:
            social["youtube"].append(href)

    for key in social:

        social[key] = list(
            dict.fromkeys(
                social[key]
            )
        )

    return social


def _parse_source_html(
    html: str,
    requested_url: str,
    final_url: str,
) -> dict:

    soup = BeautifulSoup(
        html,
        "lxml",
    )

    # ---------------------------------------------------------
    # Remove non-content elements
    # ---------------------------------------------------------

    for tag in soup(
        [
            "script",
            "style",
            "noscript",
            "svg",
            "nav",
            "footer",
        ]
    ):
        tag.decompose()

    # ---------------------------------------------------------
    # Title
    # ---------------------------------------------------------

    title = ""

    if soup.title:
        title = soup.title.get_text(
            " ",
            strip=True,
        )

    # ---------------------------------------------------------
    # Visible text
    # ---------------------------------------------------------

    text = soup.get_text(
        " ",
        strip=True,
    )

    # ---------------------------------------------------------
    # Links
    # ---------------------------------------------------------

    links = []

    for link in soup.find_all(
        "a",
        href=True,
    ):

        href = urljoin(
            final_url,
            link["href"],
        )

        links.append(
            {
                "text": link.get_text(
                    " ",
                    strip=True,
                ),
                "url": href,
            }
        )

    # ---------------------------------------------------------
    # Emails
    # ---------------------------------------------------------

    emails = _extract_emails(
        text
    )

    # ---------------------------------------------------------
    # Phones
    # ---------------------------------------------------------

    phones = _extract_phones(
        text
    )

    # ---------------------------------------------------------
    # Social links
    # ---------------------------------------------------------

    social = _extract_social_links(
        soup,
        final_url,
    )

    return {
        "requested_url": requested_url,
        "final_url": final_url,
        "title": title,
        "text": text,
        "links": links,
        "emails": emails,
        "phones": phones,
        "social": social,
        "source_type": classify_source(
            final_url
        ),
    }


def _fetch_with_httpx(
    url: str,
) -> dict:

    response = httpx.get(
        url,
        headers={
            "User-Agent": USER_AGENT,
        },
        timeout=20,
        follow_redirects=True,
    )

    response.raise_for_status()

    return _parse_source_html(
        html=response.text,
        requested_url=url,
        final_url=str(
            response.url
        ),
    )


def fetch_public_source(
    url: str,
) -> dict:

    print(
        f"[PublicSource] Fetching: {url}"
    )

    # ---------------------------------------------------------
    # Attempt 1: HTTPX
    # ---------------------------------------------------------

    try:

        result = _fetch_with_httpx(
            url
        )

        if len(result["text"]) >= 300:

            result["fetch_method"] = "httpx"
            result["fetch_status"] = "success"

            print(
                "[PublicSource] "
                "HTTPX succeeded."
            )

            return result

        print(
            "[PublicSource] "
            "HTTPX returned insufficient content."
        )

    except Exception as exc:

        print(
            f"[PublicSource] "
            f"HTTPX failed: {exc}"
        )

    # ---------------------------------------------------------
    # Attempt 2: Playwright
    # ---------------------------------------------------------

    print(
        "[PublicSource] "
        "Using Playwright fallback."
    )

    try:

        result = _fetch_with_playwright(
            url
        )

        result["fetch_method"] = "playwright"
        result["fetch_status"] = "success"

        print(
            "[PublicSource] "
            "Playwright succeeded."
        )

        return result

    except Exception as exc:

        print(
            f"[PublicSource] "
            f"Playwright failed: {exc}"
        )

        return {
            "requested_url": url,
            "final_url": None,
            "title": None,
            "text": "",
            "links": [],
            "emails": [],
            "phones": [],
            "social": {
                "linkedin": [],
                "instagram": [],
                "facebook": [],
                "youtube": [],
            },
            "source_type": classify_source(
                url
            ),
            "fetch_method": (
                "httpx+playwright"
            ),
            "fetch_status": "failed",
            "error": {
                "type": "source_fetch_failed",
                "message": str(exc),
            },
        }