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

    raw_regex = r"(?:(?:\+|00)\s*91[\s.-]?)?(?:0[\s.-]?)?(?:\d{2,5}(?:[\s.-]?\d{3,5}){1,2}|[6-9]\d{4}[\s.-]?\d{5}|[6-9]\d{9})\b"
    pattern = re.compile(raw_regex)

    matches = pattern.findall(text)
    cleaned = []
    dummy_prefixes = ("120304", "123456", "000000", "999999", "111111", "20304", "203040")

    for match in matches:
        raw = match.strip()
        # Discard copyright / date ranges like '2006-2026' or '2010 - 2024'
        if re.search(r"\b(?:19|20)\d{2}\s*[-–/]\s*(?:19|20)\d{2}\b", raw):
            continue
        digits = re.sub(r"\D", "", raw)
        if 8 <= len(digits) <= 12:
            if not any(digits.startswith(dp) or digits.endswith(dp) for dp in dummy_prefixes):
                cleaned.append(raw)

    def _phone_priority(p: str) -> int:
        d = re.sub(r"\D", "", p)
        if "+91" in p or (p.startswith("91") and len(d) == 12):
            return 0
        if len(d) == 10 and d[0] in "6789":
            return 1
        if d.startswith("0") or len(d) >= 10:
            return 2
        return 3

    seen = set()
    unique = []
    for p in sorted(cleaned, key=_phone_priority):
        norm = re.sub(r"\D", "", p)
        if norm not in seen:
            seen.add(norm)
            unique.append(p)

    return unique


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
    # 1. Extract Links, Mailto Emails, Tel Phones
    # ---------------------------------------------------------
    links = []
    emails_set = set()
    phones_set = set()

    for link in soup.find_all("a", href=True):
        raw_href = str(link.get("href", "")).strip()
        lower_href = raw_href.lower()

        if lower_href.startswith("mailto:"):
            email_val = raw_href[len("mailto:"):].split("?", 1)[0].strip()
            if email_val and "@" in email_val:
                emails_set.add(email_val)
            continue

        if lower_href.startswith("tel:"):
            phone_val = raw_href[len("tel:"):].split("?", 1)[0].strip()
            if phone_val:
                phones_set.add(phone_val)
            continue

        full_url = urljoin(final_url, raw_href)
        links.append(
            {
                "text": link.get_text(" ", strip=True),
                "url": full_url,
            }
        )

    # ---------------------------------------------------------
    # 2. Extract Social Links (from full markup)
    # ---------------------------------------------------------
    social = _extract_social_links(
        soup,
        final_url,
    )

    # ---------------------------------------------------------
    # 3. Detect About and Contact Pages (Same Domain)
    # ---------------------------------------------------------
    contact_pages = []
    about_pages = []

    contact_keywords = [
        "contact", "contact-us", "contactus", "get-in-touch", "reach-us", "connect", "reach", "enquiry", "enquiries", "contact-info"
    ]
    about_keywords = [
        "about", "about-us", "aboutus", "studio", "profile", "team", "founder", "story", "who-we-are", "info", "information", "details", "overview", "press", "studio-info", "firm-info"
    ]

    base_domain = urlparse(final_url).netloc.lower()

    for item in links:
        link_url = item["url"]
        link_text = item["text"].lower()
        if not link_url.startswith(("http://", "https://")):
            continue

        parsed_l = urlparse(link_url)
        if parsed_l.netloc and parsed_l.netloc.lower() != base_domain:
            continue

        clean_link = link_url.split("#")[0].rstrip("/")
        lower_clean = clean_link.lower()
        if "/cdn-cgi/" in lower_clean or "javascript:" in lower_clean:
            continue

        if any(k in lower_clean or k in link_text for k in contact_keywords):
            if clean_link not in contact_pages and clean_link != final_url.rstrip("/"):
                contact_pages.append(clean_link)

        if any(k in lower_clean or k in link_text for k in about_keywords):
            if clean_link not in about_pages and clean_link != final_url.rstrip("/"):
                about_pages.append(clean_link)

    # ---------------------------------------------------------
    # 4. Remove Script/Style/Noscript for Text Extraction
    # ---------------------------------------------------------
    for tag in soup(["script", "style", "noscript", "svg"]):
        tag.decompose()

    title = ""
    if soup.title:
        title = soup.title.get_text(" ", strip=True)

    text = soup.get_text(" ", strip=True)

    # Search visible content with regex
    for email in _extract_emails(text):
        emails_set.add(email)

    for phone in _extract_phones(text):
        phones_set.add(phone)

    return {
        "requested_url": requested_url,
        "final_url": final_url,
        "title": title,
        "text": text,
        "links": links,
        "emails": sorted(emails_set),
        "phones": sorted(phones_set),
        "social": social,
        "contact_pages": contact_pages,
        "about_pages": about_pages,
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
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Sec-Ch-Ua": '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Upgrade-Insecure-Requests": "1",
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

        if len(result["text"]) >= 80 or result["emails"] or result["phones"] or result["contact_pages"]:

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