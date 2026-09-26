from app.tools.rss_tool import fetch_rss_feed
from app.tools.article_filter import filter_articles
from app.tools.dedup import deduplicate_articles


def main():
    articles = fetch_rss_feed()

    filtered = filter_articles(articles)
    unique = deduplicate_articles(filtered)

    print(f"RSS articles: {len(articles)}")
    print(f"Potential residential articles: {len(filtered)}")
    print(f"Unique articles: {len(unique)}")


if __name__ == "__main__":
    main()