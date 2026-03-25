"""Event model — the core abstraction of TruthLens."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, Float, Integer, DateTime, ForeignKey, JSON
from models.base import Base


class Event(Base):
    """
    A real-world event detected from clustered articles.
    
    Events are the central node — articles, claims, entities, and timelines
    all connect through events. This enables aggregation, cross-source
    comparison, lifecycle tracking, and trust scoring.
    """
    __tablename__ = "events"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(Text, nullable=False)  # AI-generated event title
    summary = Column(Text, nullable=True)  # Multi-source synthesized summary
    category = Column(String(50), default="GENERAL", index=True)  # POLITICS, CONFLICT, ECONOMY, etc.
    status = Column(String(20), default="EMERGING", index=True)  # EMERGING, DEVELOPING, ONGOING, PEAKED, DECLINING, ARCHIVED

    # Metrics
    significance_score = Column(Float, default=0.0)  # 0-100
    trust_score = Column(Float, default=0.5)  # 0.0-1.0 aggregate
    article_count = Column(Integer, default=1)
    source_count = Column(Integer, default=1)

    # Temporal
    first_seen_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    last_updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    peak_at = Column(DateTime, nullable=True)

    # Embedding centroid for clustering
    centroid_embedding = Column(JSON, nullable=True)  # List[float]

    # Enrichment
    primary_location = Column(JSON, nullable=True)  # {name, lat, lon}
    primary_entities = Column(JSON, nullable=True)  # [{type, name}]
    sentiment_distribution = Column(JSON, nullable=True)  # {positive, negative, neutral}

    # Hierarchy (merge/split)
    parent_event_id = Column(String(36), ForeignKey("events.id"), nullable=True)
    merged_into_id = Column(String(36), ForeignKey("events.id"), nullable=True)

    metadata_ = Column("metadata", JSON, nullable=True)


class EventArticle(Base):
    """Junction table linking articles to events (many-to-many)."""
    __tablename__ = "event_articles"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    event_id = Column(String(36), ForeignKey("events.id"), nullable=False, index=True)
    article_id = Column(String(36), ForeignKey("processed_articles.id"), nullable=False, index=True)
    similarity_score = Column(Float, nullable=True)  # How similar to event centroid
    assigned_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
