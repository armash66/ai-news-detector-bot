from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.core.database import get_db
from backend.models.domain import SourceCredibility
import logging

router = APIRouter()
logger = logging.getLogger("truthlens.api.sources")

@router.get("/credibility")
async def get_all_source_credibility(db: Session = Depends(get_db)):
    """
    Returns reliability scores and bias ratings for all audited news domains.
    """
    try:
        sources = db.query(SourceCredibility).all()
        return {
            "status": "success",
            "count": len(sources),
            "data": [
                {
                    "domain": s.domain,
                    "reliability": s.reliability_score,
                    "bias": s.bias_rating,
                    "verified": s.verified_status,
                    "last_audit": s.last_audit.isoformat()
                } for s in sources
            ]
        }
    except Exception as e:
        logger.error(f"Failed to fetch source credibility: {e}")
        raise HTTPException(status_code=500, detail="Database query failed")

@router.get("/credibility/{domain}")
async def get_domain_credibility(domain: str, db: Session = Depends(get_db)):
    """
    Returns detailed forensic audit for a specific domain.
    """
    source = db.query(SourceCredibility).filter(SourceCredibility.domain == domain).first()
    if not source:
        raise HTTPException(status_code=404, detail="Domain not audited")
    
    return {
        "status": "success",
        "data": {
            "domain": source.domain,
            "reliability": source.reliability_score,
            "bias": source.bias_rating,
            "verified": source.verified_status,
            "last_audit": source.last_audit.isoformat()
        }
    }
