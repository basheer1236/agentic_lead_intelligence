import httpx
from bs4 import BeautifulSoup
from urllib.parse import quote, urljoin

AD_SEARCH_URL = "https://www.architecturaldigest.in/search/"
BASE_URL = "https://www.architecturaldigest.in"


def search_ad(query: str) -> list[dict]:
    query = query.strip()

    if not query:
        raise ValueError("Search query cannot be empty")

    url = f"{AD_SEARCH_URL}?q={quote(query)}"

    response = httpx.get(
        url,
        timeout=20,
        follow_redirects=True,
        headers={"User-Agent": "Mozilla/5.0"},
    )

    response.raise_for_status()

    soup = BeautifulSoup(response.text, "lxml")

    results = []

    for link in soup.find_all("a", href=True):
        title = link.get_text(" ", strip=True)
        href = link["href"]

        if not title:
            continue

        full_url = urljoin(BASE_URL, href)

        # Only keep useful AD content
        if (
            "/adpro/directory/profile/" in full_url
            or "/story/" in full_url
            or "/sponsored/story/" in full_url
        ):
            results.append(
                {
                    "title": title,
                    "url": full_url,
                }
            )

    # Remove duplicates
    unique_results = []
    seen_urls = set()

    for result in results:
        if result["url"] not in seen_urls:
            seen_urls.add(result["url"])
            unique_results.append(result)

    return unique_results