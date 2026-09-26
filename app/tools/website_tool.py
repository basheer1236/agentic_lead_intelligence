import re
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright


EMAIL_PATTERN = re.compile(
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
)

PHONE_PATTERN = re.compile(
    r"(?:\+?\d[\d\s().-]{7,}\d)"
)

SOCIAL_DOMAINS = {
    "linkedin": "linkedin.com",
    "instagram": "instagram.com",
    "facebook": "facebook.com",
    "youtube": "youtube.com",
}


def fetch_website(url: str) -> dict:
    """
    Fetch a verified public website.

    Strategy:
        1. HTTPX static request
        2. Playwright fallback
        3. Gracefully report source failure

    No LLM inference is performed here.
    """

    validate_url(url)

    http_error = None

    # ---------------------------------------------------------
    # STEP 1 — HTTPX
    # ---------------------------------------------------------

    try:
        result = _fetch_with_httpx(url)

        if _is_useful_result(result):
            result["fetch_method"] = "httpx"
            result["fetch_status"] = "success"
            return result

    except Exception as exc:
        http_error = str(exc)

        print(
            f"[WebsiteTool] HTTPX failed: {exc}"
        )

    # ---------------------------------------------------------
    # STEP 2 — PLAYWRIGHT FALLBACK
    # ---------------------------------------------------------

    print(
        "[WebsiteTool] Static HTML insufficient. "
        "Using Playwright fallback."
    )

    try:

        result = _fetch_with_playwright(url)

        result["fetch_method"] = "playwright"
        result["fetch_status"] = "success"

        return result

    except Exception as exc:

        print(
            f"[WebsiteTool] Playwright failed: {exc}"
        )

        # -----------------------------------------------------
        # STEP 3 — GRACEFUL FAILURE
        # -----------------------------------------------------

        return {
            "requested_url": url,
            "final_url": None,
            "title": None,
            "text": "",
            "links": [],
            "websites": [],
            "emails": [],
            "phones": [],
            "social": {
                "linkedin": [],
                "instagram": [],
                "facebook": [],
                "youtube": [],
            },
            "contact_pages": [],
            "about_pages": [],
            "fetch_method": "httpx+playwright",
            "fetch_status": "failed",
            "error": {
                "type": "website_fetch_failed",
                "httpx_error": http_error,
                "playwright_error": str(exc),
            },
        }


# =============================================================
# URL VALIDATION
# =============================================================

def validate_url(url: str) -> None:
    """
    Validate that the supplied URL is HTTP/HTTPS.
    """

    if not url:
        raise ValueError(
            "Website URL cannot be empty"
        )

    parsed = urlparse(url)

    if parsed.scheme not in {
        "http",
        "https",
    }:
        raise ValueError(
            "Website URL must use HTTP or HTTPS"
        )

    if not parsed.netloc:
        raise ValueError(
            "Invalid website URL"
        )


# =============================================================
# HTTPX
# =============================================================

def _fetch_with_httpx(url: str) -> dict:

    response = httpx.get(
        url,
        timeout=20,
        follow_redirects=True,
        headers={
            "User-Agent": "Mozilla/5.0"
        },
    )

    response.raise_for_status()

    return _parse_html(
        html=response.text,
        requested_url=url,
        final_url=str(response.url),
    )


# =============================================================
# PLAYWRIGHT
# =============================================================

def _fetch_with_playwright(url: str) -> dict:
    """
    Render JavaScript using Chromium.

    The browser starts from the verified website URL.
    """

    with sync_playwright() as playwright:

        browser = playwright.chromium.launch(
            headless=True
        )

        page = browser.new_page(
            user_agent="Mozilla/5.0"
        )

        try:

            page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=30000,
            )

            # Give client-side JavaScript a chance to render.
            page.wait_for_timeout(3000)

            html = page.content()

            final_url = page.url

        finally:
            browser.close()

    return _parse_html(
        html=html,
        requested_url=url,
        final_url=final_url,
    )


# =============================================================
# HTML PARSER
# =============================================================

def _parse_html(
    html: str,
    requested_url: str,
    final_url: str,
) -> dict:

    soup = BeautifulSoup(
        html,
        "lxml",
    )

    # ---------------------------------------------------------
    # TITLE
    # ---------------------------------------------------------

    title = None

    if soup.title:
        title = soup.title.get_text(
            " ",
            strip=True,
        )

    # ---------------------------------------------------------
    # Remove non-content elements
    # ---------------------------------------------------------

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
            final_url,
            href,
        )

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

    # ---------------------------------------------------------
    # Emails
    # ---------------------------------------------------------

    emails = set()

    for link in soup.find_all(
        "a",
        href=True,
    ):

        href = str(
            link.get("href")
        ).strip()

        if href.lower().startswith(
            "mailto:"
        ):

            email = href[
                len("mailto:")
            ].split(
                "?",
                1,
            )[0].strip()

            if EMAIL_PATTERN.fullmatch(
                email
            ):
                emails.add(
                    email
                )

    # Search visible content.
    for email in EMAIL_PATTERN.findall(
        text
    ):
        emails.add(
            email
        )

    # ---------------------------------------------------------
    # Phones
    # ---------------------------------------------------------

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

    for phone in PHONE_PATTERN.findall(
        text
    ):
        phones.add(
            " ".join(
                phone.split()
            )
        )

    # ---------------------------------------------------------
    # Social
    # ---------------------------------------------------------

    social = {
        "linkedin": [],
        "instagram": [],
        "facebook": [],
        "youtube": [],
    }

    for link in links:

        url = link["url"]
        lower_url = url.lower()

        for platform, domain in SOCIAL_DOMAINS.items():

            if domain in lower_url:

                if url not in social[platform]:

                    social[platform].append(
                        url
                    )

    # ---------------------------------------------------------
    # Contact pages
    # ---------------------------------------------------------

    contact_pages = []

    contact_keywords = [
        "contact",
        "contact-us",
        "contactus",
        "get-in-touch",
        "reach-us",
    ]

    for link in links:

        link_text = link["text"].lower()
        link_url = link["url"].lower()

        if any(
            keyword in link_text
            or keyword in link_url
            for keyword in contact_keywords
        ):

            if link["url"] not in contact_pages:

                contact_pages.append(
                    link["url"]
                )

    # ---------------------------------------------------------
    # About pages
    # ---------------------------------------------------------

    about_pages = []

    about_keywords = [
        "about",
        "about-us",
        "aboutus",
        "studio",
        "profile",
    ]

    for link in links:

        link_text = link["text"].lower()
        link_url = link["url"].lower()

        if any(
            keyword in link_text
            or keyword in link_url
            for keyword in about_keywords
        ):

            if link["url"] not in about_pages:

                about_pages.append(
                    link["url"]
                )

    # ---------------------------------------------------------
    # Website links
    # ---------------------------------------------------------

    websites = []

    ignored_domains = [
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

    return {
        "requested_url": requested_url,
        "final_url": final_url,
        "title": title,
        "text": text,
        "links": links,
        "websites": websites,
        "emails": sorted(emails),
        "phones": sorted(phones),
        "social": social,
        "contact_pages": contact_pages,
        "about_pages": about_pages,
    }


# =============================================================
# RESULT QUALITY
# =============================================================

def _is_useful_result(result: dict) -> bool:
    """
    Determine whether the static HTTP response contains enough
    meaningful content.

    This is intentionally conservative.
    """

    text = result.get(
        "text",
        "",
    )

    title = result.get(
        "title"
    )

    # Very small page = probably JS shell.
    if len(text) < 1000:
        return False

    # No title + little content = likely incomplete.
    if not title and len(text) < 2000:
        return False

    return True