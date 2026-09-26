from sqlalchemy import select
from sqlalchemy.orm import Session

from app.storage.models.article import ArticleDB


class ArticleRepository:

    @staticmethod
    def create(
        db: Session,
        url: str,
        title: str | None = None,
        author: str | None = None,
        summary: str | None = None,
        published_at=None,
        content_hash: str | None = None,
    ) -> ArticleDB:

        article = ArticleDB(
            url=url,
            title=title,
            author=author,
            summary=summary,
            published_at=published_at,
            content_hash=content_hash,
        )

        db.add(article)
        db.commit()
        db.refresh(article)

        return article

    @staticmethod
    def get_by_id(
        db: Session,
        article_id: int
    ) -> ArticleDB | None:

        statement = select(ArticleDB).where(
            ArticleDB.id == article_id
        )

        return db.scalar(statement)

    @staticmethod
    def get_by_url(
        db: Session,
        url: str
    ) -> ArticleDB | None:

        statement = select(ArticleDB).where(
            ArticleDB.url == url
        )

        return db.scalar(statement)

    @staticmethod
    def get_by_content_hash(
        db: Session,
        content_hash: str
    ) -> ArticleDB | None:

        statement = select(ArticleDB).where(
            ArticleDB.content_hash == content_hash
        )

        return db.scalar(statement)

    @staticmethod
    def get_or_create(
        db: Session,
        url: str,
        title: str | None = None,
        author: str | None = None,
        summary: str | None = None,
        published_at=None,
        content_hash: str | None = None,
    ) -> tuple[ArticleDB, bool]:

        # Check URL first
        existing = ArticleRepository.get_by_url(
            db,
            url
        )

        if existing:
            return existing, False

        # Check content hash
        if content_hash:
            existing = ArticleRepository.get_by_content_hash(
                db,
                content_hash
            )

            if existing:
                return existing, False

        # Create new article
        article = ArticleDB(
            url=url,
            title=title,
            author=author,
            summary=summary,
            published_at=published_at,
            content_hash=content_hash,
        )

        db.add(article)
        db.commit()
        db.refresh(article)

        return article, True