import logging
import feedparser
from typing import List, Dict
import time

logger = logging.getLogger("truthlens.ingestion.news")

class RSSFeedCrawler:
    def __init__(self, feed_urls: List[str] = None):
        """
        Initializes the RSS spider. In production, this pulls from PostgreSQL configurations.
        """
        self.feed_urls = feed_urls or [
            "http://feeds.bbci.co.uk/news/world/rss.xml",
            "https://rss.nytimes.com/services/xml/rss/nyt/World.xml"
        ]
        logger.info(f"Initialized RSSFeedCrawler with {len(self.feed_urls)} global sources.")

    def fetch_latest_intelligence(self) -> List[Dict]:
        """
        Scrapes open source news feeds and restructures them for the TruthLens processing queue.
        """
        harvested_intel = []
        for url in self.feed_urls:
            try:
                feed = feedparser.parse(url)
                logger.info(f"Parsed {len(feed.entries)} entries from {url}")
                for entry in feed.entries[:5]: # Take top 5 for prototyping
                    harvested_intel.append({
                        "source": feed.feed.title if hasattr(feed.feed, 'title') else url,
                        "title": entry.title,
                        "summary_text": entry.summary if hasattr(entry, 'summary') else "",
                        "url": entry.link,
                        "timestamp": entry.published if hasattr(entry, 'published') else time.time()
                    })
            except Exception as e:
                logger.error(f"Error harvesting from {url}: {e}")
                
        return harvested_intel
