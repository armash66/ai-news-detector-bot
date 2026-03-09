import time
import feedparser
from sqlalchemy.orm import Session
from backend.database import SessionLocal, ArticleModel
from backend.scrapers.article_scraper import ArticleScraper
from backend.services.analyzer import ArticleAnalyzer
from backend.utils.logger import get_logger

logger = get_logger("news_fetcher")

# A small list of RSS feeds to monitor
RSS_FEEDS = [
    "http://feeds.bbci.co.uk/news/world/rss.xml",
    "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
    # Add more sources here, reliable or unreliable
]

def fetch_and_analyze_news():
    """Background task to fetch news, analyze it, and store in DB."""
    logger.info("Starting background news fetch...")
    scraper = ArticleScraper()
    # Lazy load analyzer to avoid blocking startup if not needed
    analyzer = ArticleAnalyzer()
    
    db: Session = SessionLocal()
    
    try:
        for feed_url in RSS_FEEDS:
            logger.info(f"Fetching RSS feed: {feed_url}")
            feed = feedparser.parse(feed_url)
            
            # Process up to 3 recent articles per feed to save time/compute during demo
            for entry in feed.entries[:3]:
                url = entry.link
                
                # Check if already processed
                existing = db.query(ArticleModel).filter(ArticleModel.url == url).first()
                if existing:
                    continue
                
                logger.debug(f"Scraping new article: {url}")
                scraped = scraper.scrape(url)
                
                if scraped.success and scraped.content:
                    # Analyze it
                    logger.debug(f"Analyzing article: {scraped.title}")
                    try:
                        report = analyzer.analyze_url(url, explain=True)
                        
                        # Save to DB
                        db_article = ArticleModel(
                            url=url,
                            title=scraped.title,
                            author=", ".join(scraped.authors) if scraped.authors else None,
                            source=scraped.source_domain,
                            text_content=scraped.content,
                            image_url=scraped.top_image,
                            credibility_score=report.credibility.score,
                            verdict=report.credibility.verdict,
                            claims=[c.model_dump() for c in report.claims],
                            evidence=[e.model_dump() for e in report.evidence],
                            component_scores=report.credibility.component_scores
                        )
                        db.add(db_article)
                        db.commit()
                        logger.info(f"Saved analyzed article: {scraped.title[:50]}...")
                    except Exception as e:
                        logger.error(f"Failed to analyze/save {url}: {str(e)}")
                        db.rollback()
                        
    except Exception as e:
        logger.error(f"Error in news fetcher: {str(e)}")
    finally:
        db.close()
        logger.info("Background news fetch completed.")
