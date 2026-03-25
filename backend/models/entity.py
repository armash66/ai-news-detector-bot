"""Entity models — knowledge graph nodes and mention tracking."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, Float, DateTime, ForeignKey, JSON
from models.base import Base


class Entity(Base):
    """Canonical entity in the knowledge graph (person, org, location, etc.)."""
    __tablename__ = "entities"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    canonical_name = Column(String(255), nullable=False, index=True)
    entity_type = Column(String(50), nullable=False, index=True)  # PERSON, ORG, LOCATION, CONCEPT
    aliases = Column(JSON, nullable=True)  # ["Biden", "POTUS", "President Biden"]
    description = Column(Text, nullable=True)
    wikidata_id = Column(String(50), nullable=True)
    metadata_ = Column("metadata", JSON, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class EntityMention(Base):
    """Individual mention of an entity within an article."""
    __tablename__ = "entity_mentions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    entity_id = Column(String(36), ForeignKey("entities.id"), nullable=False, index=True)
    article_id = Column(String(36), ForeignKey("processed_articles.id"), nullable=False, index=True)
    event_id = Column(String(36), ForeignKey("events.id"), nullable=True, index=True)
    mention_text = Column(String(255), nullable=False)
    context_snippet = Column(Text, nullable=True)
    salience_score = Column(Float, default=0.0)
