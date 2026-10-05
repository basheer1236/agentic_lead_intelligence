import os
import ssl
import logging
from sqlalchemy import create_engine
from sqlalchemy.engine.url import make_url
from sqlalchemy.orm import sessionmaker

from app.config.settings import settings
from app.storage.base import Base
import app.storage.models  # Ensure all models are registered

logger = logging.getLogger(__name__)


def get_effective_database_url(raw_url: str) -> str:
    """
    Normalizes database URL for cloud (Neon PostgreSQL) and local PostgreSQL.
    - Normalizes legacy postgres:// to postgresql:// (required by SQLAlchemy 2.0+)
    - Provider-independent: works with local PostgreSQL and Neon PostgreSQL
    - Provides automatic fallback to pure-Python pg8000 driver if native psycopg C binaries
      fail to load on restricted Windows environments (WDAC / AppLocker)
    """
    url = (raw_url or "").strip()
    if not url:
        return "postgresql://postgres:postgres@localhost:5432/lead_intelligence"

    # Normalize dialect prefix
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)

    # Check for native driver availability if targeting PostgreSQL
    if url.startswith("postgresql://") and not (
        url.startswith("postgresql+pg8000://") or url.startswith("postgresql+psycopg://")
    ):
        try:
            import psycopg
            from psycopg import pq
        except Exception as exc:
            logger.info("Native psycopg binary not available (%s); falling back to pure-Python pg8000 driver.", exc)
            url = url.replace("postgresql://", "postgresql+pg8000://", 1)

    return url


def get_engine(database_url: str | None = None):
    """
    Construct a cloud-ready SQLAlchemy engine.
    Applies cloud connection resilience settings (pool_pre_ping, pool_recycle)
    specifically optimized for serverless Neon PostgreSQL and local PostgreSQL.
    """
    url_str = get_effective_database_url(database_url or settings.database_url)
    engine_kwargs = {
        "pool_pre_ping": True,  # Discards dropped/stale connections (essential for Neon serverless)
    }

    if "postgresql" in url_str:
        # Cloud PostgreSQL pooling (Neon serverless scale-to-zero safe)
        engine_kwargs["pool_recycle"] = 300   # 5-minute connection recycle
        engine_kwargs["pool_size"] = 5
        engine_kwargs["max_overflow"] = 10

        # If pg8000 is used with SSL query params, translate to ssl_context
        if "pg8000" in url_str:
            parsed = make_url(url_str)
            query_params = dict(parsed.query)
            needs_ssl = query_params.pop("sslmode", None) in ("require", "verify-ca", "verify-full")
            query_params.pop("channel_binding", None)

            clean_url = parsed.set(query=query_params)
            url_str = str(clean_url)

            connect_args = engine_kwargs.get("connect_args", {})
            if needs_ssl:
                connect_args["ssl_context"] = ssl.create_default_context()
            engine_kwargs["connect_args"] = connect_args

    elif url_str.startswith("sqlite"):
        engine_kwargs["connect_args"] = {"check_same_thread": False}

    return create_engine(url_str, **engine_kwargs)


# Active SQLAlchemy engine
engine = get_engine()

# Active Session factory
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


def init_db(bind_engine=None):
    """
    Ensures all database tables and relationships exist in Neon PostgreSQL or local PostgreSQL.
    Safe to call repeatedly (idempotent DDL).
    """
    target = bind_engine or engine
    try:
        Base.metadata.create_all(target)
        logger.info("Database tables verified and ready.")
        return True
    except Exception as exc:
        logger.warning("Database table creation deferred: %s", exc)
        return False


def reset_db_engine(database_url: str | None = None):
    """
    Rebinds SQLAlchemy engine and SessionLocal to a new database URL at runtime.
    Used when user updates connection settings without restarting the server.
    """
    global engine, SessionLocal
    engine = get_engine(database_url)
    SessionLocal.configure(bind=engine)
    return engine