from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from backend.core.database import get_db
from backend.models.domain import Article, Claim
import logging

router = APIRouter()
logger = logging.getLogger("truthlens.api.feed")

@router.get("/live")
async def get_live_intelligence_feed(db: Session = Depends(get_db)):
    """
    Retrieves the latest structured data from the PostgreSQL intelligence database.
    """
    logger.info("Fetching latest intelligence from persistence layer.")
    try:
        # Fetch top 15 most recent articles
        articles = db.query(Article).order_by(Article.published_at.desc()).limit(15).all()
        
        processed_feed = []
        for article in articles:
            # Check for associated claim to get severity/suspicion
            claim = db.query(Claim).filter(Claim.article_id == article.id).first()
            
            # Simple simulation of score if claim doesn't exist yet
            severity = "Medium"
            suspicion = 30.0
            if claim:
                severity = "Critical" if any(word in article.title.lower() for word in ["war", "bomb", "cyber", "attack", "dead"]) else "Medium"
                suspicion = 88.0 if severity == "Critical" else 32.0
                
            processed_feed.append({
                "id": article.id,
                "source": article.source_domain,
                "content_preview": article.title,
                "severity": severity,
                "timestamp": article.published_at.isoformat(),
                "suspicion_score": suspicion,
            })
            
        return {"status": "success", "count": len(processed_feed), "data": processed_feed}
    except Exception as e:
        logger.error(f"Failed to fetch feed from DB: {e}")
        raise HTTPException(status_code=500, detail=str(e))
