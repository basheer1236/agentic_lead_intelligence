from app.storage.base import Base
from app.storage.database import engine

from app.storage.models.article import ArticleDB
from app.storage.models.project import ProjectDB
from app.storage.models.designer import DesignerDB
from app.storage.models.source import SourceDB


Base.metadata.create_all(
    bind=engine,
    tables=[SourceDB.__table__]
)

print("Sources table created successfully.")