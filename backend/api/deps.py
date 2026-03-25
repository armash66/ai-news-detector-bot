"""API Dependencies — shared FastAPI dependency injection."""

from fastapi import Depends
from sqlalchemy.orm import Session
from models.database import get_db


def get_database() -> Session:
    """Database session dependency for API routes."""
    return Depends(get_db)
