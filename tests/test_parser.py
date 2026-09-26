from app.tools.rss_tool import fetch_rss_feed
from app.tools.article_filter import filter_articles
from app.tools.dedup import deduplicate_articles
from app.tools.http_tool import fetch_article
from app.tools.article_parser import parse_article


def main():
    articles = deduplicate_articles(
        filter_articles(fetch_rss_feed())
    )

    article = articles[0]

    html = fetch_article(article["url"])

    parsed = parse_article(html)

    print("Title:", parsed["title"])
    print("Author:", parsed["author"])
    print("Description:", parsed["description"])

    print("\nText characters:", len(parsed["text"]))

    print("\nFirst 1000 characters:\n")
    print(parsed["text"][:1000])

    print("\nLinks found:", len(parsed["links"]))

    for link in parsed["links"][:10]:
        print(link)


if __name__ == "__main__":
    main()