import logging
import feedparser
import httpx

logger = logging.getLogger(__name__)

RSS_URL = "https://www.architecturaldigest.in/feed/rss"


def fetch_rss_feed():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    feed = None
    try:
        resp = httpx.get(RSS_URL, headers=headers, timeout=12.0, follow_redirects=True)
        resp.raise_for_status()
        feed = feedparser.parse(resp.text)
    except Exception as exc:
        logger.warning(f"httpx fetch failed for RSS feed: {exc}")
        try:
            feed = feedparser.parse(RSS_URL, request_headers=headers)
        except Exception as parse_err:
            logger.error(f"feedparser direct parse failed: {parse_err}")
            feed = None

    articles = []

    if feed and hasattr(feed, "entries"):
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