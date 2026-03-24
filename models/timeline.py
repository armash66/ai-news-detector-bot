"""Timeline model — ordered development entries within an event."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, Float, DateTime, ForeignKey
from src.models.base import Base


class TimelineEntry(Base):
    """A single development milestone in an event's lifecycle."""
    __tablename__ = "timeline_entries"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    event_id = Column(String(36), ForeignKey("events.id"), nullable=False, index=True)
    source_id = Column(String(36), ForeignKey("sources.id"), nullable=True)
    article_id = Column(String(36), ForeignKey("processed_articles.id"), nullable=True)
    timestamp = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    description = Column(Text, nullable=False)
    entry_type = Column(String(30), default="UPDATE")  # INITIAL_REPORT, UPDATE, CORRECTION, ESCALATION, DE_ESCALATION
    significance = Column(Float, default=0.5)
