from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from backend.core.config import settings
import logging

logger = logging.getLogger("truthlens.db")

# Setup connection string. Fallback to sqlite if postgres is unavailable locally for fast prototyping.
try:
    if settings.USE_SQLITE_FALLBACK:
        engine = create_engine(settings.SQLITE_URL, connect_args={"check_same_thread": False})
        logger.info("Using local SQLite database for prototyping.")
    else:
        engine = create_engine(settings.SQLALCHEMY_DATABASE_URI)
        logger.info(f"Connecting to PostgreSQL at {settings.POSTGRES_SERVER}")
        
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()

except Exception as e:
    logger.error(f"Failed to connect to database: {e}")
    raise e

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
