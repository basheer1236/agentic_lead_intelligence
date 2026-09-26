from app.storage.base import Base
from app.storage.database import engine

from app.storage.models.article import ArticleDB


Base.metadata.create_all(
    bind=engine,
    tables=[
        ArticleDB.__table__
    ],
)

print("Articles table created successfully.")