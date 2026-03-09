from fastapi import APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.database import SessionLocal, ArticleModel

router = APIRouter()

@router.get("/feed")
def get_news_feed(limit: int = 10, offset: int = 0):
    """Retrieve the latest monitored and analyzed news articles."""
    db: Session = SessionLocal()
    try:
        articles = db.query(ArticleModel).order_by(ArticleModel.created_at.desc()).offset(offset).limit(limit).all()
        return [
            {
                "id": a.id,
                "title": a.title,
                "url": a.url,
                "source": a.source,
                "published_date": a.published_date,
                "credibility_score": a.credibility_score,
                "verdict": a.verdict,
                "image_url": a.image_url,
                "scraped_at": a.created_at.isoformat()
            }
            for a in articles
        ]
    finally:
        db.close()

@router.get("/stats")
def get_platform_stats():
    """Retrieve high-level statistics of platform operation."""
    db: Session = SessionLocal()
    try:
        total_scraped = db.query(func.count(ArticleModel.id)).scalar()
        
        # Breakdown by verdict
        credible = db.query(func.count(ArticleModel.id)).filter(ArticleModel.verdict == "Likely Credible").scalar()
        mixed = db.query(func.count(ArticleModel.id)).filter(ArticleModel.verdict == "Mixed Credibility").scalar()
        fake = db.query(func.count(ArticleModel.id)).filter(ArticleModel.verdict == "Likely Misinformation").scalar()
        
        return {
            "total_articles_monitored": total_scraped,
            "verdict_distribution": {
                "credible": credible,
                "mixed": mixed,
                "fake": fake
            }
        }
    finally:
        db.close()
