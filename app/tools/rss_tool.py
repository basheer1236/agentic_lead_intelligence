import logging
import feedparser
import httpx
from bs4 import BeautifulSoup
from typing import List, Dict

logger = logging.getLogger(__name__)

PRIMARY_RSS_URL = "https://www.architecturaldigest.in/feed/rss"
FALLBACK_PAGES = [
    "https://www.architecturaldigest.in/topic/homes",
    "https://www.architecturaldigest.in/interiors",
    "https://www.architecturaldigest.in/architecture",
]

BROWSER_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


def _scrape_ad_html(url: str) -> List[Dict[str, str]]:
    """Scrape article metadata directly from Architectural Digest India section pages."""
    articles = []
    try:
        resp = httpx.get(url, headers=BROWSER_HEADERS, timeout=10.0, follow_redirects=True)
        if resp.status_code != 200:
            return []
        soup = BeautifulSoup(resp.text, "html.parser")
        
        # Look for article cards and summary headlines
        for link in soup.find_all("a", href=True):
            href = link["href"]
            if not href.startswith("http"):
                href = f"https://www.architecturaldigest.in{href}"
            
            # Match story / story / content links
            if "/story/" in href or "/gallery/" in href:
                title = link.get_text(strip=True)
                if len(title) > 20 and not any(a["url"] == href for a in articles):
                    articles.append({
                        "title": title,
                        "url": href,
                        "summary": title,
                        "published": None,
                        "author": "Architectural Digest India",
                    })
                    if len(articles) >= 30:
                        break
    except Exception as exc:
        logger.warning(f"Failed to scrape fallback page {url}: {exc}")
    return articles


def fetch_rss_feed() -> List[Dict[str, str]]:
    """
    Fetch articles from Architectural Digest India RSS feed with high resilience.
    If RSS is rate-limited or blocked, gracefully falls back to direct section scraping.
    """
    feed = None
    articles = []

    # Attempt 1: Fetch RSS XML via HTTPX
    try:
        resp = httpx.get(PRIMARY_RSS_URL, headers=BROWSER_HEADERS, timeout=10.0, follow_redirects=True)
        if resp.status_code == 200 and len(resp.text) > 200:
            feed = feedparser.parse(resp.text)
    except Exception as exc:
        logger.warning(f"httpx RSS fetch encountered error: {exc}")

    # Attempt 2: Direct feedparser parse
    if not feed or not getattr(feed, "entries", None):
        try:
            feed = feedparser.parse(PRIMARY_RSS_URL, request_headers=BROWSER_HEADERS)
        except Exception as exc:
            logger.warning(f"Direct feedparser parse error: {exc}")
            feed = None

    # Parse RSS entries if available
    if feed and hasattr(feed, "entries") and len(feed.entries) > 0:
        for entry in feed.entries:
            title = entry.get("title")
            url = entry.get("link")
            if title and url:
                articles.append({
                    "title": title,
                    "url": url,
                    "summary": entry.get("summary", ""),
                    "published": entry.get("published"),
                    "author": entry.get("author", "Architectural Digest India"),
                })

    # Attempt 3: If RSS yielded 0 articles, use direct section scraping fallback
    if not articles:
        logger.info("RSS feed returned 0 entries. Falling back to direct AD India section scraping...")
        for page_url in FALLBACK_PAGES:
            scraped = _scrape_ad_html(page_url)
            for sc in scraped:
                if not any(a["url"] == sc["url"] for a in articles):
                    articles.append(sc)
            if len(articles) >= 25:
                break

    return articles