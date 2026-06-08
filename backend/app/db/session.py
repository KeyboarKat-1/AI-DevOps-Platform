from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


def _make_engine(url: str):
    return create_engine(url, pool_pre_ping=True, future=True)


# Primary database URL from settings
PRIMARY_DB_URL = settings.DATABASE_URL
# Fallback to a local SQLite file if the primary DB is unreachable
FALLBACK_SQLITE_URL = "sqlite:///./devops_fallback.db"


# Try to create an engine and verify a simple connection. If it fails,
# fall back to a lightweight SQLite engine so the app can keep running.
try:
    engine = _make_engine(PRIMARY_DB_URL)
    # quick connection test
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    logger.info("Connected to primary database: %s", PRIMARY_DB_URL)
except SQLAlchemyError as exc:
    logger.error("Primary DB connection failed: %s", exc)
    logger.warning("Falling back to SQLite database at %s", FALLBACK_SQLITE_URL)
    engine = _make_engine(FALLBACK_SQLITE_URL)


# SessionLocal is a factory that produces new Session objects for each request.
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    future=True,
)
