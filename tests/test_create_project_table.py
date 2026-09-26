from app.storage.base import Base
from app.storage.database import engine

from app.storage.models.article import ArticleDB
from app.storage.models.project import ProjectDB


Base.metadata.create_all(
    bind=engine,
    tables=[
        ProjectDB.__table__
    ],
)

print("Projects table created successfully.")