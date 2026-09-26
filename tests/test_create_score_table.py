from app.storage.base import Base
from app.storage.database import engine

from app.storage.models.article import ArticleDB
from app.storage.models.project import ProjectDB
from app.storage.models.designer import DesignerDB
from app.storage.models.source import SourceDB
from app.storage.models.rug import RugDB
from app.storage.models.score import ScoreDB


Base.metadata.create_all(
    bind=engine,
    tables=[ScoreDB.__table__]
)

print("Scores table created successfully.")