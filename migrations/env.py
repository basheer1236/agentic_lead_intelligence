from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

from app.config.settings import settings
from app.storage.base import Base

from app.storage.models.article import ArticleDB
from app.storage.models.project import ProjectDB
from app.storage.models.designer import DesignerDB
from app.storage.models.source import SourceDB
from app.storage.models.rug import RugDB
from app.storage.models.score import ScoreDB


# Alembic Config object
config = context.config


# Configure logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


# SQLAlchemy metadata for Alembic autogenerate
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in offline mode."""

    url = settings.database_url

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in online mode."""

    # Get Alembic configuration
    configuration = config.get_section(
        config.config_ini_section,
        {}
    )

    # Use DATABASE_URL from .env instead of storing
    # the database password inside alembic.ini
    configuration["sqlalchemy.url"] = settings.database_url

    # Create SQLAlchemy engine
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    # Connect to PostgreSQL
    with connectable.connect() as connection:

        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()