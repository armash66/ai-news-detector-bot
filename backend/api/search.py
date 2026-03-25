"""Search API Router — unified search endpoint."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from models.database import get_db
from search.engine import SearchEngine
from schemas.schemas import EventResponse, SearchResponse

router = APIRouter()
search_engine = SearchEngine()


@router.get("", response_model=SearchResponse)
def search(
    q: str = Query(..., min_length=1, max_length=500, description="Search query"),
    type: str = Query("keyword", description="Search type: keyword, semantic, hybrid"),
    category: Optional[str] = Query(None),
    min_trust: Optional[float] = Query(None, ge=0, le=1),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Search events by keyword, semantic similarity, or hybrid approach."""
    filters = {}
    if category:
        filters["category"] = category
    if min_trust is not None:
        filters["min_trust"] = min_trust

    results = search_engine.search(
        query=q, db=db, search_type=type,
        filters=filters, page=page, limit=limit,
    )

    return SearchResponse(
        data=[EventResponse.model_validate(e) for e in results["events"]],
        meta={
            "total": results["total"],
            "page": results["page"],
            "limit": results["limit"],
            "search_type": type,
        },
    )
