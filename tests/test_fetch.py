from app.tools.rss_tool import fetch_rss_feed
from app.tools.article_filter import filter_articles
from app.tools.dedup import deduplicate_articles
from app.tools.http_tool import fetch_article


def main():
    articles = deduplicate_articles(
        filter_articles(fetch_rss_feed())
    )

    article = articles[0]

    html = fetch_article(article["url"])

    print("URL:", article["url"])
    print("HTML characters:", len(html))
    print("\nFirst 500 characters:\n")
    print(html[:500])


if __name__ == "__main__":
    main()  