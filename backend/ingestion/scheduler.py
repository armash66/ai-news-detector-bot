"""Ingestion Scheduler — orchestrates all connectors on configurable intervals."""

import asyncio
import logging
from datetime import datetime, timezone
from typing import List

from sqlalchemy.orm import Session
from models.database import SessionLocal
from models.source import Source
from models.article import RawArticle
from ingestion.base import BaseConnector, RawArticleInput
from ingestion.rss import RSSConnector
from utils.hashing import compute_content_hash
from config.settings import settings

logger = logging.getLogger("truthlens.ingestion.scheduler")


class IngestionScheduler:
    """Runs connectors on schedule, deduplicates, and persists raw articles."""

    def __init__(self):
        self.connectors: List[BaseConnector] = []
        self.interval = settings.INGESTION_INTERVAL_SECONDS
        self._setup_default_connectors()

    def _setup_default_connectors(self):
        """Initialize default connectors."""
        self.connectors.append(RSSConnector())
        logger.info(f"Initialized {len(self.connectors)} connectors")

    def register_connector(self, connector: BaseConnector):
        """Add a custom connector at runtime."""
        self.connectors.append(connector)
        logger.info(f"Registered connector: {connector}")

    async def run_cycle(self) -> int:
        """Run one ingestion cycle across all connectors. Returns count of new articles."""
        total_new = 0

        for connector in self.connectors:
            try:
                articles = await connector.fetch()
                saved = self._persist_articles(articles)
                total_new += saved
                logger.info(f"[{connector.name}] Fetched {len(articles)}, saved {saved} new")
            except Exception as e:
                logger.error(f"[{connector.name}] Cycle failed: {e}")

        return total_new

    def _persist_articles(self, articles: List[RawArticleInput]) -> int:
        """Deduplicate and save articles to database. Returns count of new articles."""
        db: Session = SessionLocal()
        saved_count = 0

        try:
            for article in articles:
                content_hash = compute_content_hash(article.content)

                # Dedup: check content hash and URL
                existing = (
                    db.query(RawArticle)
                    .filter(
                        (RawArticle.content_hash == content_hash)
                        | (RawArticle.url == article.url)
                    )
                    .first()
                )

                if existing:
                    continue

                # Ensure source exists
                source = db.query(Source).filter(Source.domain == article.source_domain).first()
                if not source:
                    source = Source(
                        domain=article.source_domain,
                        name=article.source_name,
                        source_type="RSS",
                        reliability_score=0.5,
                    )
                    db.add(source)
                    db.flush()

                # Save raw article
                raw = RawArticle(
                    source_id=source.id,
                    url=article.url,
                    title=article.title,
                    raw_content=article.content,
                    author=article.author,
                    published_at=article.published_at,
                    content_hash=content_hash,
                    processing_status="PENDING",
                    metadata_=article.metadata,
                )
                db.add(raw)
                saved_count += 1

            db.commit()
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to persist articles: {e}")
        finally:
            db.close()

        return saved_count

    async def run_forever(self):
        """Continuous ingestion loop."""
        logger.info(f"Ingestion scheduler started (interval: {self.interval}s)")
        while True:
            try:
                new_count = await self.run_cycle()
                logger.info(f"Cycle complete — {new_count} new articles ingested")
            except Exception as e:
                logger.error(f"Ingestion cycle error: {e}")

            await asyncio.sleep(self.interval)
