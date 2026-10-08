import logging
import feedparser
import httpx

logger = logging.getLogger(__name__)

RSS_URL = "https://www.architecturaldigest.in/feed/rss"


def fetch_rss_feed():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        resp = httpx.get(RSS_URL, headers=headers, timeout=20.0, follow_redirects=True)
        resp.raise_for_status()
        feed = feedparser.parse(resp.text)
    except Exception as exc:
        logger.warning(f"httpx fetch failed for RSS feed, falling back to direct feedparser parse: {exc}")
        feed = feedparser.parse(RSS_URL)

    articles = []

    for entry in feed.entries:
        articles.append(
            {
                "title": entry.get("title"),
                "url": entry.get("link"),
                "summary": entry.get("summary"),
                "published": entry.get("published"),
                "author": entry.get("author"),
            }
        )

    return articles