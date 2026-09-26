import feedparser

RSS_URL = "https://www.architecturaldigest.in/feed/rss"


def fetch_rss_feed():
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