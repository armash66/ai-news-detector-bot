"""Sources API Router — source credibility endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.models.database import get_db
from src.models.source import Source
from src.schemas.schemas import SourceResponse
from src.trust.engine import SourceScorer

router = APIRouter()
source_scorer = SourceScorer()


@router.get("")
def list_sources(db: Session = Depends(get_db)):
    """List all sources with credibility scores."""
    sources = db.query(Source).order_by(Source.reliability_score.desc()).all()
    return {
        "data": [SourceResponse.model_validate(s) for s in sources],
        "meta": {"count": len(sources)},
    }


@router.get("/{domain}/score")
def get_source_score(domain: str, db: Session = Depends(get_db)):
    """Get detailed credibility score for a specific source."""
    source = db.query(Source).filter(Source.domain.ilike(f"%{domain}%")).first()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")

    score = source_scorer.score_source(source)
    bias = source_scorer.get_bias_rating(source)

    return {
        "domain": source.domain,
        "name": source.name,
        "reliability_score": score,
        "bias_rating": bias,
        "is_verified": source.is_verified,
        "article_count": "N/A",
    }
