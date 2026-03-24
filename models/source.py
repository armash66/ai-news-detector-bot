"""Source model — represents a news source (domain/publisher)."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Boolean, DateTime, Text, JSON
from src.models.base import Base


class Source(Base):
    __tablename__ = "sources"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    domain = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    source_type = Column(String(50), nullable=False, default="RSS")  # RSS, API, SCRAPER
    reliability_score = Column(Float, default=0.5)  # 0.0 - 1.0
    bias_rating = Column(String(50), default="UNKNOWN")  # LEFT, CENTER_LEFT, CENTER, CENTER_RIGHT, RIGHT
    country = Column(String(10), nullable=True)  # ISO country code
    language = Column(String(10), default="en")
    is_verified = Column(Boolean, default=False)
    feed_url = Column(Text, nullable=True)  # RSS/API endpoint
    scrape_config = Column(JSON, nullable=True)  # CSS selectors, etc.
    metadata_ = Column("metadata", JSON, nullable=True)
    last_fetched_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
