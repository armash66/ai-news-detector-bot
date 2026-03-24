"""Trending API Router — trending events and topics."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta

from src.models.database import get_db
from src.models.event import Event
from src.schemas.schemas import EventResponse

router = APIRouter()


@router.get("")
def get_trending(
    hours: int = Query(24, ge=1, le=168, description="Time window in hours"),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    """Get trending events ranked by velocity (article growth rate)."""
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)

    events = (
        db.query(Event)
        .filter(
            Event.status.notin_(["ARCHIVED", "MERGED"]),
            Event.last_updated_at >= cutoff,
        )
        .order_by(Event.significance_score.desc())
        .limit(limit)
        .all()
    )

    return {
        "data": [EventResponse.model_validate(e) for e in events],
        "meta": {"window_hours": hours, "count": len(events)},
    }


@router.get("/topics")
def get_trending_topics(
    limit: int = Query(10, ge=1, le=20),
    db: Session = Depends(get_db),
):
    """Get hot topic categories."""
    from sqlalchemy import func

    topics = (
        db.query(Event.category, func.count(Event.id).label("count"))
        .filter(Event.status.notin_(["ARCHIVED", "MERGED"]))
        .group_by(Event.category)
        .order_by(func.count(Event.id).desc())
        .limit(limit)
        .all()
    )

    return {
        "data": [{"category": t[0], "event_count": t[1]} for t in topics],
        "meta": {"count": len(topics)},
    }
