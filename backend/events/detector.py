"""Event Detector — assigns articles to events using embedding similarity + spike detection."""

import logging
from typing import List, Optional, Tuple
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from models.event import Event, EventArticle
from models.article import ProcessedArticle
from models.timeline import TimelineEntry
from nlp.embeddings import EmbeddingGenerator
from config.settings import settings
from utils.time_utils import is_within_window

logger = logging.getLogger("truthlens.events.detector")


class EventDetector:
    """
    Core event detection engine.
    
    Hybrid approach:
    1. Compare new article embedding against active event centroids
    2. If match found (cosine > threshold) → attach to event
    3. If no match → create new event
    """

    def __init__(self):
        self.similarity_threshold = settings.EVENT_SIMILARITY_THRESHOLD
        self.time_window_hours = settings.EVENT_TIME_WINDOW_HOURS
        self.embedder = EmbeddingGenerator()

    def detect_and_assign(self, article: ProcessedArticle, db: Session) -> Event:
        """
        Detect which event an article belongs to, or create a new one.
        
        Args:
            article: ProcessedArticle with embedding_vector populated
            db: Database session
            
        Returns:
            The Event this article was assigned to
        """
        if not article.embedding_vector:
            logger.warning(f"Article {article.id} has no embedding, creating standalone event")
            return self._create_event(article, db)

        # Get all active events (not ARCHIVED or MERGED)
        active_events = (
            db.query(Event)
            .filter(Event.status.notin_(["ARCHIVED", "MERGED"]))
            .filter(Event.centroid_embedding.isnot(None))
            .all()
        )

        # Find best matching event
        best_match, best_score = self._find_best_match(article, active_events)

        if best_match and best_score >= self.similarity_threshold:
            # Check time window
            if is_within_window(best_match.last_updated_at, self.time_window_hours):
                logger.info(
                    f"Article matched event '{best_match.title[:50]}' "
                    f"(similarity: {best_score:.3f})"
                )
                self._attach_to_event(article, best_match, best_score, db)
                return best_match

        # No match — create new event
        event = self._create_event(article, db)
        logger.info(f"Created new event: '{event.title[:50]}'")
        return event

    def _find_best_match(
        self,
        article: ProcessedArticle,
        events: List[Event],
    ) -> Tuple[Optional[Event], float]:
        """Find the event with highest cosine similarity to article embedding."""
        best_event = None
        best_score = 0.0

        article_embedding = article.embedding_vector

        for event in events:
            if not event.centroid_embedding:
                continue

            score = self.embedder.cosine_similarity(
                article_embedding, event.centroid_embedding
            )

            if score > best_score:
                best_score = score
                best_event = event

        return best_event, best_score

    def _attach_to_event(
        self,
        article: ProcessedArticle,
        event: Event,
        similarity: float,
        db: Session,
    ):
        """Attach an article to an existing event and update event metadata."""
        # Create junction record
        link = EventArticle(
            event_id=event.id,
            article_id=article.id,
            similarity_score=similarity,
        )
        db.add(link)

        # Update article's event_id
        article.event_id = event.id

        # Update event metrics
        event.article_count += 1
        event.last_updated_at = datetime.now(timezone.utc)

        # Recalculate centroid (running average)
        if event.centroid_embedding and article.embedding_vector:
            import numpy as np
            old = np.array(event.centroid_embedding)
            new = np.array(article.embedding_vector)
            n = event.article_count
            updated = ((old * (n - 1)) + new) / n
            event.centroid_embedding = updated.tolist()

        # Update source count (check if this is a new source)
        existing_sources = (
            db.query(ProcessedArticle.source_id)
            .join(EventArticle, EventArticle.article_id == ProcessedArticle.id)
            .filter(EventArticle.event_id == event.id)
            .distinct()
            .count()
        )
        event.source_count = existing_sources

        # Update event status based on article velocity
        self._update_event_status(event)

        # Add timeline entry
        timeline = TimelineEntry(
            event_id=event.id,
            source_id=article.source_id,
            article_id=article.id,
            description=f"New report: {article.clean_text[:100]}..." if article.clean_text else "New article added",
            entry_type="UPDATE",
            significance=similarity,
        )
        db.add(timeline)

        db.flush()

    def _create_event(self, article: ProcessedArticle, db: Session) -> Event:
        """Create a new event from a seed article."""
        # Generate event title from article
        title = article.clean_text[:120] if article.clean_text else "Unnamed Event"
        # Try to use the article's summary as event summary
        summary = article.summary or title

        event = Event(
            title=title,
            summary=summary,
            status="EMERGING",
            significance_score=10.0,
            article_count=1,
            source_count=1,
            centroid_embedding=article.embedding_vector,
            primary_entities=article.entities_extracted,
            primary_location=(article.locations[0] if article.locations else None),
        )
        db.add(event)
        db.flush()

        # Link article to event
        article.event_id = event.id
        link = EventArticle(
            event_id=event.id,
            article_id=article.id,
            similarity_score=1.0,
        )
        db.add(link)

        # Create initial timeline entry
        timeline = TimelineEntry(
            event_id=event.id,
            source_id=article.source_id,
            article_id=article.id,
            description=f"First reported: {title[:100]}",
            entry_type="INITIAL_REPORT",
            significance=1.0,
        )
        db.add(timeline)

        db.flush()
        return event

    def _update_event_status(self, event: Event):
        """Update event lifecycle status based on metrics."""
        if event.article_count >= 20 and event.source_count >= 5:
            if event.status in ("EMERGING", "DEVELOPING"):
                event.status = "ONGOING"
        elif event.article_count >= 5 and event.source_count >= 3:
            if event.status == "EMERGING":
                event.status = "DEVELOPING"

        # Update significance based on article count and source diversity
        event.significance_score = min(
            100.0,
            event.article_count * 3 + event.source_count * 10,
        )
