from app.tools.rss_tool import fetch_rss_feed
from app.tools.article_filter import filter_articles
from app.tools.dedup import deduplicate_articles
from app.tools.http_tool import fetch_article
from app.tools.article_parser import parse_article
from app.agents.rug_agent import RugIntelligenceAgent


def main():

    articles = deduplicate_articles(
        filter_articles(fetch_rss_feed())
    )

    article = articles[0]

    html = fetch_article(article["url"])
    parsed = parse_article(html)

    agent = RugIntelligenceAgent()

    result = agent.analyze(
        title=parsed["title"],
        text=parsed["text"],
    )

    print("\nRug Intelligence:")
    print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    main()