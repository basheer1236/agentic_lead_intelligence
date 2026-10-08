import logging
import feedparser
import httpx
from typing import List, Dict

logger = logging.getLogger(__name__)

RSS_URL = "https://www.architecturaldigest.in/feed/rss"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/rss+xml, application/xml, text/xml;q=0.9, */*;q=0.8",
}


def fetch_rss_feed() -> List[Dict[str, str]]:
    """
    Connect exclusively to Architectural Digest India RSS feed and extract article entries.
    """
    feed = None

    try:
        resp = httpx.get(RSS_URL, headers=HEADERS, timeout=15.0, follow_redirects=True)
        resp.raise_for_status()
        feed = feedparser.parse(resp.text)
    except Exception as exc:
        logger.warning(f"HTTP fetch of RSS XML failed ({exc}), falling back to direct feedparser parse.")
        try:
            feed = feedparser.parse(RSS_URL, request_headers=HEADERS)
        except Exception as err:
            logger.error(f"Direct feedparser parse failed: {err}")
            feed = None

    articles = []

    if feed and hasattr(feed, "entries"):
        for entry in feed.entries:
            title = entry.get("title")
            url = entry.get("link")
            if title and url:
                articles.append(
                    {
                        "title": title,
                        "url": url,
                        "summary": entry.get("summary", ""),
                        "published": entry.get("published"),
                        "author": entry.get("author", "Architectural Digest India"),
                    }
                )

    return articles