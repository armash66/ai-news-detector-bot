"""Events API Router — core event endpoints."""

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from models.database import get_db
from models.event import Event, EventArticle
from models.article import ProcessedArticle
from models.timeline import TimelineEntry
from models.claim import Claim
from schemas.schemas import EventResponse, EventListResponse, ArticleResponse, TimelineEntryResponse, ClaimResponse
from trust.engine import ArticleScorer, ContradictionDetector

router = APIRouter()


@router.get("", response_model=EventListResponse)
def list_events(
    status: Optional[str] = Query(None, description="Filter by status"),
    category: Optional[str] = Query(None, description="Filter by category"),
    min_trust: Optional[float] = Query(None, ge=0, le=1),
    sort: str = Query("-significance", description="Sort field: -significance, -updated, -articles"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """List events with filtering, sorting, and pagination."""
    query = db.query(Event).filter(Event.status != "MERGED")

    if status:
        query = query.filter(Event.status == status)
    if category:
        query = query.filter(Event.category == category)
    if min_trust is not None:
        query = query.filter(Event.trust_score >= min_trust)

    # Sorting
    if sort == "-significance":
        query = query.order_by(Event.significance_score.desc())
    elif sort == "-updated":
        query = query.order_by(Event.last_updated_at.desc())
    elif sort == "-articles":
        query = query.order_by(Event.article_count.desc())
    else:
        query = query.order_by(Event.last_updated_at.desc())

    total = query.count()
    offset = (page - 1) * limit
    events = query.offset(offset).limit(limit).all()

    return EventListResponse(
        data=[EventResponse.model_validate(e) for e in events],
        meta={"total": total, "page": page, "limit": limit},
    )


@router.get("/{event_id}")
def get_event(event_id: str, db: Session = Depends(get_db)):
    """Get full event detail with articles, timeline, and claims."""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    # Get articles
    articles = (
        db.query(ProcessedArticle)
        .join(EventArticle, EventArticle.article_id == ProcessedArticle.id)
        .filter(EventArticle.event_id == event_id)
        .order_by(ProcessedArticle.processed_at.desc())
        .all()
    )

    # Get timeline
    timeline = (
        db.query(TimelineEntry)
        .filter(TimelineEntry.event_id == event_id)
        .order_by(TimelineEntry.timestamp.asc())
        .all()
    )

    # Get claims
    claims = (
        db.query(Claim)
        .filter(Claim.event_id == event_id)
        .all()
    )

    return {
        "event": EventResponse.model_validate(event),
        "articles": [ArticleResponse(
            id=a.id,
            title=a.clean_text[:100] if a.clean_text else "",
            summary=a.summary,
            sentiment_score=a.sentiment_score,
            credibility_score=a.credibility_score,
            language=a.language or "en",
        ) for a in articles],
        "timeline": [TimelineEntryResponse.model_validate(t) for t in timeline],
        "claims": [ClaimResponse.model_validate(c) for c in claims],
    }


@router.get("/{event_id}/trust")
def get_event_trust(event_id: str, db: Session = Depends(get_db)):
    """Get trust analysis for an event with explainability."""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    # Detect contradictions
    detector = ContradictionDetector()
    contradictions = detector.find_contradictions(event_id, db)

    return {
        "event_id": event_id,
        "trust_score": event.trust_score,
        "article_count": event.article_count,
        "source_count": event.source_count,
        "sentiment_distribution": event.sentiment_distribution,
        "contradictions": contradictions,
        "explanation": f"Trust score based on {event.source_count} independent sources and {event.article_count} articles",
    }
