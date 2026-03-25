"""Article models — RawArticle (ingested) and ProcessedArticle (NLP-enriched)."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, Float, Integer, DateTime, ForeignKey, JSON
from models.base import Base


class RawArticle(Base):
    """Raw article as ingested from a source, before NLP processing."""
    __tablename__ = "raw_articles"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    source_id = Column(String(36), ForeignKey("sources.id"), nullable=False, index=True)
    url = Column(Text, unique=True, nullable=False)
    title = Column(Text, nullable=False)
    raw_content = Column(Text, nullable=False)
    author = Column(String(255), nullable=True)
    published_at = Column(DateTime, nullable=True)
    fetched_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    content_hash = Column(String(64), unique=True, nullable=False, index=True)  # SHA-256
    processing_status = Column(String(20), default="PENDING", index=True)  # PENDING, PROCESSING, DONE, FAILED
    failure_reason = Column(Text, nullable=True)
    metadata_ = Column("metadata", JSON, nullable=True)


class ProcessedArticle(Base):
    """Article after NLP pipeline — embeddings, entities, sentiment extracted."""
    __tablename__ = "processed_articles"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    raw_article_id = Column(String(36), ForeignKey("raw_articles.id"), unique=True, nullable=False)
    source_id = Column(String(36), ForeignKey("sources.id"), nullable=False, index=True)
    event_id = Column(String(36), ForeignKey("events.id"), nullable=True, index=True)

    # Cleaned content
    clean_text = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)
    language = Column(String(10), default="en")
    word_count = Column(Integer, default=0)

    # NLP outputs
    embedding_vector = Column(JSON, nullable=True)  # List[float] — stored as JSON for SQLite compat, pgvector in prod
    entities_extracted = Column(JSON, nullable=True)  # [{type, value, salience}]
    locations = Column(JSON, nullable=True)  # [{name, lat, lon}]
    topics = Column(JSON, nullable=True)  # [topic_labels]

    # Scores
    sentiment_score = Column(Float, nullable=True)  # -1.0 to 1.0
    bias_score = Column(Float, nullable=True)  # 0.0 to 1.0
    credibility_score = Column(Float, nullable=True)  # 0.0 to 1.0

    processed_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
