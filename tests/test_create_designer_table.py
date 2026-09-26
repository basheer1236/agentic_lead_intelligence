from app.storage.base import Base
from app.storage.database import engine

from app.storage.models.article import ArticleDB
from app.storage.models.project import ProjectDB
from app.storage.models.designer import DesignerDB


Base.metadata.create_all(
    bind=engine,
    tables=[DesignerDB.__table__]
)

print("Designers table created successfully.")