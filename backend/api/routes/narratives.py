from fastapi import APIRouter
import datetime
import random

router = APIRouter()

@router.get("/clusters")
async def get_narrative_clusters():
    """
    Returns high-level narrative clusters identified by the VLM and semantic analysis.
    In production, this would use UMAP/HDBSCAN on sentence embeddings from the news feed.
    """
    clusters = [
        {
            "id": "narr_1",
            "topic": "Coordinated Energy Crisis Narratives",
            "volume": 1240,
            "growth": 14.5,
            "dominant_sentiment": "Fear",
            "sources": ["Social Media", "Alternative News", "Telegram"],
            "verification_status": "Highly Manipulated",
            "last_active": (datetime.datetime.now() - datetime.timedelta(minutes=5)).isoformat()
        },
        {
            "topic": "Central Bank Digital Currency Propaganda",
            "volume": 850,
            "growth": -5.2,
            "dominant_sentiment": "Distrust",
            "sources": ["Global News", "X (Twitter)"],
            "verification_status": "Mixed/Organic",
            "last_active": (datetime.datetime.now() - datetime.timedelta(minutes=12)).isoformat()
        },
        {
            "topic": "AI Regulation Misinformation",
            "volume": 2100,
            "growth": 32.1,
            "dominant_sentiment": "Alarmism",
            "sources": ["Substack", "YouTube", "Mainstream Media"],
            "verification_status": "Bot Amplified",
            "last_active": (datetime.datetime.now() - datetime.timedelta(minutes=2)).isoformat()
        }
    ]
    
    return {
        "status": "success",
        "timestamp": datetime.datetime.now().isoformat(),
        "total_active_narratives": len(clusters),
        "data": clusters
    }
