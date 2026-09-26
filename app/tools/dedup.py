from app.utils.hashing import generate_content_hash


def deduplicate_articles(articles: list[dict]) -> list[dict]:
    seen_urls = set()
    seen_hashes = set()

    unique_articles = []

    for article in articles:
        url = article.get("url")
        title = article.get("title", "")
        summary = article.get("summary", "")

        content = f"{title}|{summary}"
        content_hash = generate_content_hash(content)

        if url in seen_urls:
            continue

        if content_hash in seen_hashes:
            continue

        article["content_hash"] = content_hash

        seen_urls.add(url)
        seen_hashes.add(content_hash)

        unique_articles.append(article)

    return unique_articles