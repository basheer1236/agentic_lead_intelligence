from app.storage.database import SessionLocal
from app.storage.repositories.article_repository import ArticleRepository


def main():
    db = SessionLocal()

    try:
        url = "https://example.com/dedup-test"
        content_hash = "dedup_hash_001"

        # First insertion
        article1, created1 = ArticleRepository.get_or_create(
            db=db,
            url=url,
            title="Deduplication Test",
            content_hash=content_hash,
        )

        print("First call:")
        print("Article ID:", article1.id)
        print("Created:", created1)

        # Second insertion with exactly the same data
        article2, created2 = ArticleRepository.get_or_create(
            db=db,
            url=url,
            title="Deduplication Test",
            content_hash=content_hash,
        )

        print("\nSecond call:")
        print("Article ID:", article2.id)
        print("Created:", created2)

        # Verify same database record
        print("\nSame article ID:", article1.id == article2.id)

    finally:
        db.close()


if __name__ == "__main__":
    main()