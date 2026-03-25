"""Alert model — triggered notifications for significant events."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, JSON
from models.base import Base


class Alert(Base):
    """System-generated alert triggered by event rules (trend spike, trust anomaly, etc.)."""
    __tablename__ = "alerts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    event_id = Column(String(36), ForeignKey("events.id"), nullable=True, index=True)
    alert_type = Column(String(30), nullable=False, index=True)  # NEW_EVENT, TREND_SPIKE, TRUST_ANOMALY, CONTRADICTION
    severity = Column(String(10), default="MEDIUM")  # LOW, MEDIUM, HIGH, CRITICAL
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    triggered_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    acknowledged = Column(Boolean, default=False)
    metadata_ = Column("metadata", JSON, nullable=True)
