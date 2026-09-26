from app.tools.rss_tool import fetch_rss_feed
from app.tools.article_filter import filter_articles
from app.tools.dedup import deduplicate_articles
from app.tools.http_tool import fetch_article
from app.tools.article_parser import parse_article
from app.agents.relevance_agent import RelevanceAgent


def main():
    import sys
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    articles = deduplicate_articles(
        filter_articles(fetch_rss_feed())
    )

    article = articles[0]

    html = fetch_article(article["url"])
    parsed = parse_article(html)

    agent = RelevanceAgent()

    result = agent.classify(
        title=parsed["title"],
        description=parsed["description"],
        text=parsed["text"],
    )

    print("\nRelevance Result:")
    print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    main()