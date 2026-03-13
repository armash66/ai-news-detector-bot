from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.core.database import get_db
from backend.models.domain import Article, Narrative
import datetime

router = APIRouter()

@router.get("/clusters")
async def get_narrative_clusters(db: Session = Depends(get_db)):
    """
    Returns real narrative clusters identified during global OSINT ingestion.
    """
    try:
        # Fetch all narratives
        narratives = db.query(Narrative).all()
        
        clusters = []
        for narr in narratives:
            # Count articles in this narrative
            count = db.query(func.count(Article.id)).filter(Article.narrative_id == narr.id).scalar()
            
            # Simulated sentiment and verification for prototype
            clusters.append({
                "id": narr.id,
                "topic": narr.topic,
                "volume": count,
                "growth": 5.0, # Placeholder growth
                "dominant_sentiment": "Alert" if count > 5 else "Neutral",
                "sources": [narr.origin_source],
                "verification_status": "Bot Amplified" if count > 8 else "Pending Investigation",
                "last_active": narr.created_at.isoformat()
            })
            
        return {
            "status": "success",
            "timestamp": datetime.datetime.now().isoformat(),
            "total_active_narratives": len(clusters),
            "data": clusters
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.get("/{narrative_id}/tree")
async def get_narrative_tree(narrative_id: str, db: Session = Depends(get_db)):
    """
    Returns the publication sequence for a narrative to visualize origin and propagation.
    """
    try:
        articles = db.query(Article).filter(Article.narrative_id == narrative_id).order_by(Article.published_at.asc()).all()
        
        sequence = []
        for i, art in enumerate(articles):
            sequence.append({
                "id": art.id,
                "title": art.title,
                "source": art.source_domain,
                "timestamp": art.published_at.isoformat(),
                "node_type": "Origin" if i == 0 else "Propagation",
                # Simulate a 'parent' link for the tree structure
                "parent_id": articles[max(0, i-1)].id if i > 0 else None
            })
            
        return {
            "status": "success",
            "narrative_id": narrative_id,
            "nodes": sequence
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
