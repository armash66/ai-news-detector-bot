"""Search Engine — keyword + semantic search with trust-aware ranking."""

import logging
from typing import List, Dict, Any, Optional

from sqlalchemy.orm import Session
from sqlalchemy import or_

from src.models.event import Event
from src.models.article import ProcessedArticle
from src.nlp.embeddings import EmbeddingGenerator
from src.config.settings import settings

logger = logging.getLogger("truthlens.search")


class SearchEngine:
    """Unified search across events and articles with keyword + semantic modes."""

    def __init__(self):
        self.embedder = EmbeddingGenerator()

    def search(
        self,
        query: str,
        db: Session,
        search_type: str = "keyword",
        filters: Optional[Dict[str, Any]] = None,
        page: int = 1,
        limit: int = 20,
    ) -> Dict[str, Any]:
        """
        Unified search endpoint.
        
        Args:
            query: Search query string
            db: Database session
            search_type: "keyword", "semantic", or "hybrid"
            filters: Optional filters {category, status, min_trust, etc.}
            page: Page number (1-indexed)
            limit: Results per page
        """
        filters = filters or {}

        if search_type == "semantic":
            results = self._semantic_search(query, db, filters, page, limit)
        elif search_type == "hybrid":
            keyword_results = self._keyword_search(query, db, filters, page, limit * 2)
            semantic_results = self._semantic_search(query, db, filters, page, limit * 2)
            results = self._merge_results(keyword_results, semantic_results, limit)
        else:
            results = self._keyword_search(query, db, filters, page, limit)

        return results

    def _keyword_search(
        self,
        query: str,
        db: Session,
        filters: Dict[str, Any],
        page: int,
        limit: int,
    ) -> Dict[str, Any]:
        """Full-text keyword search across event titles and summaries."""
        q = db.query(Event).filter(
            Event.status != "MERGED",
            or_(
                Event.title.ilike(f"%{query}%"),
                Event.summary.ilike(f"%{query}%"),
            ),
        )

        # Apply filters
        q = self._apply_filters(q, filters)

        # Order by significance (trust-aware)
        q = q.order_by(Event.significance_score.desc())

        total = q.count()
        offset = (page - 1) * limit
        events = q.offset(offset).limit(limit).all()

        return {
            "events": events,
            "total": total,
            "page": page,
            "limit": limit,
        }

    def _semantic_search(
        self,
        query: str,
        db: Session,
        filters: Dict[str, Any],
        page: int,
        limit: int,
    ) -> Dict[str, Any]:
        """Semantic search — encode query and find nearest event centroids."""
        query_embedding = self.embedder.encode(query)

        # Get all active events with centroids
        q = db.query(Event).filter(
            Event.status != "MERGED",
            Event.centroid_embedding.isnot(None),
        )
        q = self._apply_filters(q, filters)
        events = q.all()

        # Score each event by cosine similarity
        scored_events = []
        for event in events:
            if event.centroid_embedding:
                similarity = self.embedder.cosine_similarity(
                    query_embedding, event.centroid_embedding
                )
                # Trust-aware ranking
                trust_boost = (event.trust_score or 0.5) * 0.25
                recency_boost = 0.1  # Could be time-decay based
                final_score = similarity * 0.5 + trust_boost + recency_boost + \
                    (event.significance_score or 0) / 100 * 0.15
                scored_events.append((event, final_score))

        # Sort by score
        scored_events.sort(key=lambda x: x[1], reverse=True)

        total = len(scored_events)
        offset = (page - 1) * limit
        page_results = scored_events[offset: offset + limit]

        return {
            "events": [e[0] for e in page_results],
            "total": total,
            "page": page,
            "limit": limit,
        }

    def _apply_filters(self, query, filters: Dict[str, Any]):
        """Apply optional filters to event query."""
        if "category" in filters:
            query = query.filter(Event.category == filters["category"])
        if "status" in filters:
            query = query.filter(Event.status == filters["status"])
        if "min_trust" in filters:
            query = query.filter(Event.trust_score >= filters["min_trust"])
        if "min_significance" in filters:
            query = query.filter(Event.significance_score >= filters["min_significance"])
        return query

    def _merge_results(
        self,
        keyword_results: Dict,
        semantic_results: Dict,
        limit: int,
    ) -> Dict[str, Any]:
        """Merge keyword and semantic results, deduplicating by event ID."""
        seen = set()
        merged = []

        # Interleave: keyword first, then semantic
        for event in keyword_results["events"]:
            if event.id not in seen:
                seen.add(event.id)
                merged.append(event)

        for event in semantic_results["events"]:
            if event.id not in seen:
                seen.add(event.id)
                merged.append(event)

        return {
            "events": merged[:limit],
            "total": len(merged),
            "page": 1,
            "limit": limit,
        }
