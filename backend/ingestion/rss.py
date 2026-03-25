"""RSS Feed Connector — ingests articles from RSS/Atom feeds."""

import asyncio
from datetime import datetime, timezone
from typing import List, Dict, Any
from urllib.parse import urlparse
import feedparser
import logging

from ingestion.base import BaseConnector, RawArticleInput

logger = logging.getLogger("truthlens.ingestion.rss")

# Default global RSS feeds for news intelligence
DEFAULT_FEEDS: List[Dict[str, str]] = [
    {"url": "http://feeds.bbci.co.uk/news/world/rss.xml", "name": "BBC World News"},
    {"url": "https://rss.nytimes.com/services/xml/rss/nyt/World.xml", "name": "NYT World"},
    {"url": "https://feeds.reuters.com/reuters/worldNews", "name": "Reuters World"},
    {"url": "https://www.aljazeera.com/xml/rss/all.xml", "name": "Al Jazeera"},
    {"url": "https://rss.cnn.com/rss/edition_world.rss", "name": "CNN World"},
    {"url": "https://www.theguardian.com/world/rss", "name": "The Guardian World"},
    {"url": "https://feeds.washingtonpost.com/rss/world", "name": "Washington Post World"},
    {"url": "https://timesofindia.indiatimes.com/rssfeeds/296589292.cms", "name": "Times of India"},
]


class RSSConnector(BaseConnector):
    """Fetches and normalizes articles from RSS/Atom feeds."""

    def __init__(self, feeds: List[Dict[str, str]] | None = None, max_per_feed: int = 20):
        super().__init__(name="rss", source_type="RSS")
        self.feeds = feeds or DEFAULT_FEEDS
        self.max_per_feed = max_per_feed

    async def fetch(self) -> List[RawArticleInput]:
        """Fetch latest articles from all configured RSS feeds."""
        all_articles: List[RawArticleInput] = []

        for feed_config in self.feeds:
            try:
                articles = await self._fetch_single_feed(feed_config)
                all_articles.extend(articles)
                self.logger.info(f"Fetched {len(articles)} articles from {feed_config['name']}")
            except Exception as e:
                self.logger.error(f"Failed to fetch {feed_config['name']}: {e}")

        self.logger.info(f"Total RSS articles fetched: {len(all_articles)}")
        return all_articles

    async def _fetch_single_feed(self, feed_config: Dict[str, str]) -> List[RawArticleInput]:
        """Parse a single RSS feed and return normalized articles."""
        url = feed_config["url"]
        source_name = feed_config["name"]

        # feedparser is synchronous — run in executor to avoid blocking
        loop = asyncio.get_event_loop()
        feed = await loop.run_in_executor(None, feedparser.parse, url)

        if feed.bozo and not feed.entries:
            raise ConnectionError(f"Failed to parse feed: {url}")

        domain = urlparse(url).netloc
        articles: List[RawArticleInput] = []

        for entry in feed.entries[: self.max_per_feed]:
            # Extract published date
            published = None
            if hasattr(entry, "published_parsed") and entry.published_parsed:
                try:
                    published = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
                except Exception:
                    pass

            # Extract content (prefer full content, fallback to summary)
            content = ""
            if hasattr(entry, "content") and entry.content:
                content = entry.content[0].get("value", "")
            elif hasattr(entry, "summary"):
                content = entry.summary or ""

            # Extract author
            author = getattr(entry, "author", None)

            articles.append(
                RawArticleInput(
                    url=entry.link,
                    title=entry.title,
                    content=content,
                    source_domain=domain,
                    source_name=source_name,
                    author=author,
                    published_at=published,
                    metadata={
                        "feed_url": url,
                        "categories": [t.get("term", "") for t in getattr(entry, "tags", [])],
                    },
                )
            )

        return articles

    async def health_check(self) -> bool:
        """Check if at least one feed is reachable."""
        try:
            loop = asyncio.get_event_loop()
            feed = await loop.run_in_executor(
                None, feedparser.parse, self.feeds[0]["url"]
            )
            return len(feed.entries) > 0
        except Exception:
            return False
