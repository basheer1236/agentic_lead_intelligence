import httpx
from bs4 import BeautifulSoup
from urllib.parse import urljoin

AD_DIRECTORY_URL = "https://www.architecturaldigest.in/adpro/directory/"


def fetch_ad_directory() -> str:
    response = httpx.get(
        AD_DIRECTORY_URL,
        timeout=20,
        follow_redirects=True,
        headers={"User-Agent": "Mozilla/5.0"},
    )
    response.raise_for_status()
    return response.text


def find_directory_profile(
    html: str,
    designer_name: str | None = None,
    studio_name: str | None = None,
) -> dict | None:

    soup = BeautifulSoup(html, "lxml")

    queries = []

    if designer_name:
        queries.append(designer_name.strip().lower())

    if studio_name:
        queries.append(studio_name.strip().lower())

    # Only inspect actual AD PRO profile links
    profile_links = soup.find_all(
        "a",
        href=lambda href: href and "/adpro/directory/profile/" in href,
    )

    for link in profile_links:

        text = link.get_text(" ", strip=True).lower()

        for query in queries:

            if query and query in text:
                return {
                    "found": True,
                    "matched_query": query,
                    "matched_name": link.get_text(" ", strip=True),
                    "profile_url": urljoin(
                        AD_DIRECTORY_URL,
                        link["href"],
                    ),
                }

    return None