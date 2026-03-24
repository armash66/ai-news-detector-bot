"""Event Merger — handles merge and split logic for events."""

import logging
from typing import List, Tuple
from datetime import datetime, timezone

import numpy as np
from sqlalchemy.orm import Session

from src.models.event import Event, EventArticle
from src.models.article import ProcessedArticle
from src.models.timeline import TimelineEntry
from src.nlp.embeddings import EmbeddingGenerator
from src.config.settings import settings

logger = logging.getLogger("truthlens.events.merger")


class EventMerger:
    """Handles event merge and split operations."""

    def __init__(self):
        self.merge_threshold = settings.EVENT_MERGE_THRESHOLD
        self.embedder = EmbeddingGenerator()

    def find_merge_candidates(self, db: Session) -> List[Tuple[Event, Event, float]]:
        """Find pairs of events that should be merged based on centroid similarity."""
        active_events = (
            db.query(Event)
            .filter(Event.status.notin_(["ARCHIVED", "MERGED"]))
            .filter(Event.centroid_embedding.isnot(None))
            .all()
        )

        candidates = []
        for i, event_a in enumerate(active_events):
            for event_b in active_events[i + 1:]:
                similarity = self.embedder.cosine_similarity(
                    event_a.centroid_embedding,
                    event_b.centroid_embedding,
                )
                if similarity >= self.merge_threshold:
                    candidates.append((event_a, event_b, similarity))
                    logger.info(
                        f"Merge candidate: '{event_a.title[:30]}' + '{event_b.title[:30]}' "
                        f"(sim: {similarity:.3f})"
                    )

        return candidates

    def merge_events(self, primary: Event, secondary: Event, db: Session) -> Event:
        """
        Merge secondary event into primary. Primary absorbs all articles.
        
        Args:
            primary: The event that survives (usually larger)
            secondary: The event that gets absorbed
            db: Database session
            
        Returns:
            The merged (primary) event
        """
        logger.info(f"Merging '{secondary.title[:40]}' into '{primary.title[:40]}'")

        # Reassign all articles from secondary to primary
        secondary_links = (
            db.query(EventArticle)
            .filter(EventArticle.event_id == secondary.id)
            .all()
        )

        for link in secondary_links:
            link.event_id = primary.id
            # Also update the processed article
            article = db.query(ProcessedArticle).filter(
                ProcessedArticle.id == link.article_id
            ).first()
            if article:
                article.event_id = primary.id

        # Recalculate centroid
        if primary.centroid_embedding and secondary.centroid_embedding:
            p = np.array(primary.centroid_embedding)
            s = np.array(secondary.centroid_embedding)
            pw = primary.article_count
            sw = secondary.article_count
            merged_centroid = (p * pw + s * sw) / (pw + sw)
            primary.centroid_embedding = merged_centroid.tolist()

        # Update metrics
        primary.article_count += secondary.article_count
        primary.source_count = max(primary.source_count, secondary.source_count)
        primary.last_updated_at = datetime.now(timezone.utc)

        # Mark secondary as merged
        secondary.status = "MERGED"
        secondary.merged_into_id = primary.id

        # Add timeline entry
        entry = TimelineEntry(
            event_id=primary.id,
            description=f"Merged with related event: {secondary.title[:80]}",
            entry_type="UPDATE",
            significance=0.8,
        )
        db.add(entry)

        db.flush()
        return primary

    def check_and_split(self, event: Event, db: Session) -> List[Event]:
        """
        Check if an event should be split into sub-events.
        Uses intra-cluster variance analysis.
        
        Returns list of resulting events (original + new children).
        """
        if event.article_count < 6:  # Too few articles to split
            return [event]

        # Get all article embeddings for this event
        articles = (
            db.query(ProcessedArticle)
            .join(EventArticle, EventArticle.article_id == ProcessedArticle.id)
            .filter(EventArticle.event_id == event.id)
            .filter(ProcessedArticle.embedding_vector.isnot(None))
            .all()
        )

        if len(articles) < 6:
            return [event]

        embeddings = [a.embedding_vector for a in articles if a.embedding_vector]
        if len(embeddings) < 6:
            return [event]

        # Try K-means with K=2
        try:
            from sklearn.cluster import KMeans
            from sklearn.metrics import silhouette_score

            X = np.array(embeddings)
            kmeans = KMeans(n_clusters=2, random_state=42, n_init=10)
            labels = kmeans.fit_predict(X)

            sil_score = silhouette_score(X, labels)

            if sil_score < settings.EVENT_SPLIT_SILHOUETTE_THRESHOLD:
                return [event]  # Not separable enough

            # Count articles per cluster
            cluster_0 = [a for a, l in zip(articles, labels) if l == 0]
            cluster_1 = [a for a, l in zip(articles, labels) if l == 1]

            if len(cluster_0) < 3 or len(cluster_1) < 3:
                return [event]  # Clusters too small

            logger.info(
                f"Splitting event '{event.title[:40]}' "
                f"(silhouette: {sil_score:.3f}, clusters: {len(cluster_0)}/{len(cluster_1)})"
            )

            # Create child event for the smaller cluster
            smaller = cluster_1 if len(cluster_0) >= len(cluster_1) else cluster_0
            child = Event(
                title=f"[Split] {smaller[0].clean_text[:100] if smaller[0].clean_text else 'Sub-event'}",
                summary=f"Sub-event split from: {event.title[:80]}",
                status="DEVELOPING",
                parent_event_id=event.id,
                article_count=len(smaller),
                source_count=len(set(a.source_id for a in smaller)),
                centroid_embedding=np.mean([a.embedding_vector for a in smaller], axis=0).tolist(),
            )
            db.add(child)
            db.flush()

            # Reassign articles
            for article in smaller:
                article.event_id = child.id
                link = db.query(EventArticle).filter(
                    EventArticle.article_id == article.id,
                    EventArticle.event_id == event.id,
                ).first()
                if link:
                    link.event_id = child.id

            # Update parent metrics
            remaining = len(articles) - len(smaller)
            event.article_count = remaining
            event.last_updated_at = datetime.now(timezone.utc)

            db.flush()
            return [event, child]

        except ImportError:
            logger.warning("scikit-learn not available for split analysis")
            return [event]
        except Exception as e:
            logger.error(f"Split analysis failed: {e}")
            return [event]
