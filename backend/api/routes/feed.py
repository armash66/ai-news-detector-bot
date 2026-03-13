from fastapi import APIRouter, HTTPException
import logging
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
from ingestion.news_crawler import RSSFeedCrawler

router = APIRouter()
logger = logging.getLogger("truthlens.api.feed")
crawler = RSSFeedCrawler()

@router.get("/live")
async def get_live_intelligence_feed():
    """
    Retrieves the latest structured data from the OSINT fetchers.
    In a full production cluster, this would query the indexed PostgreSQL or Vector database.
    Because we are scaffolding, it actively invokes the crawler.
    """
    logger.info("Executing live OSINT scatter-gather operation.")
    try:
        latest_intel = crawler.fetch_latest_intelligence()
        # Add some mock AI analysis data for demonstration.
        processed_feed = []
        for i, article in enumerate(latest_intel):
            processed_feed.append({
                "id": str(i),
                "source": article["source"],
                "content_preview": article["title"],
                "severity": "Critical" if "war" in article["title"].lower() or "bomb" in article["title"].lower() else "Medium",
                "timestamp": article["timestamp"],
                "suspicion_score": 85.0 if "Critical" in article["title"] else 30.0,
            })
            
        return {"status": "success", "count": len(processed_feed), "data": processed_feed}
    except Exception as e:
        logger.error(f"Failed to fetch feed: {e}")
        raise HTTPException(status_code=500, detail="Intelligence feed retrieval failed.")
