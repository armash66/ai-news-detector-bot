"""
TruthLens v3 - Database Connection Layer

Supports PostgreSQL (production) with SQLite fallback (development).
Provides both sync and async session factories.
"""

import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from src.config.settings import settings

logger = logging.getLogger("truthlens.db")


def _build_engine():
    """Create the SQLAlchemy engine based on configuration."""
    if settings.USE_SQLITE:
        logger.info("Using SQLite for local development.")
        return create_engine(
            settings.SQLITE_URL,
            connect_args={"check_same_thread": False},
            echo=settings.DEBUG,
        )
    else:
        logger.info(f"Connecting to PostgreSQL at {settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}")
        return create_engine(
            settings.DATABASE_URL,
            pool_size=20,
            max_overflow=10,
            pool_pre_ping=True,
            echo=settings.DEBUG,
        )


engine = _build_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    """FastAPI dependency — yields a database session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
