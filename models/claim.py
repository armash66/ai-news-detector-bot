"""Claim model — factual assertions extracted from articles."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, Float, Integer, DateTime, ForeignKey, JSON
from src.models.base import Base


class Claim(Base):
    """Factual claim extracted from an article, linked to an event for cross-source verification."""
    __tablename__ = "claims"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    event_id = Column(String(36), ForeignKey("events.id"), nullable=True, index=True)
    article_id = Column(String(36), ForeignKey("processed_articles.id"), nullable=False, index=True)
    claim_text = Column(Text, nullable=False)
    claim_type = Column(String(20), default="FACTUAL")  # FACTUAL, OPINION, PREDICTION
    verdict = Column(String(20), default="UNVERIFIED")  # VERIFIED, FALSE, UNVERIFIED, DISPUTED
    confidence = Column(Float, nullable=True)
    supporting_sources = Column(Integer, default=0)
    contradicting_sources = Column(Integer, default=0)
    evidence = Column(JSON, nullable=True)  # [{article_id, stance, snippet}]
    extracted_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
