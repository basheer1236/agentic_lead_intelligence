from app.storage.database import SessionLocal
from app.storage.repositories.article_repository import ArticleRepository


def main():
    db = SessionLocal()

    try:
        # Get or create a test article
        article, _ = ArticleRepository.get_or_create(
            db=db,
            url="https://example.com/test-article",
            title="Test Residential Project",
            author="Test Author",
            summary="Test article for repository validation.",
            content_hash="test_hash_001",
        )

        print("Article created:")
        print("ID:", article.id)
        print("Title:", article.title)

        # Find by URL
        found_article = ArticleRepository.get_by_url(
            db,
            "https://example.com/test-article"
        )

        print("\nArticle found by URL:")
        print("ID:", found_article.id if found_article else None)
        print("Title:", found_article.title if found_article else None)

        # Find by content hash
        hash_article = ArticleRepository.get_by_content_hash(
            db,
            "test_hash_001"
        )

        print("\nArticle found by content hash:")
        print("ID:", hash_article.id if hash_article else None)

        # Find by ID
        id_article = ArticleRepository.get_by_id(
            db,
            article.id
        )

        print("\nArticle found by ID:")
        print("ID:", id_article.id if id_article else None)

    finally:
        db.close()


if __name__ == "__main__":
    main()