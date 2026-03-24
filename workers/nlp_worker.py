"""NLP Worker — processes raw articles through the NLP pipeline and event detection."""

import logging
import asyncio
from datetime import datetime, timezone

from sqlalchemy.orm import Session
from src.models.database import SessionLocal
from src.models.article import RawArticle, ProcessedArticle
from src.models.source import Source
from src.nlp.pipeline import NLPPipeline
from src.events.detector import EventDetector
from src.trust.engine import ArticleScorer, SourceScorer

logger = logging.getLogger("truthlens.workers.nlp")


class NLPWorker:
    """Processes pending raw articles through NLP pipeline and event detection."""

    def __init__(self):
        self.pipeline = NLPPipeline()
        self.event_detector = EventDetector()
        self.article_scorer = ArticleScorer()
        self.source_scorer = SourceScorer()

    def process_pending(self, batch_size: int = 10) -> int:
        """Process a batch of pending raw articles. Returns count processed."""
        db: Session = SessionLocal()
        processed_count = 0

        try:
            pending = (
                db.query(RawArticle)
                .filter(RawArticle.processing_status == "PENDING")
                .limit(batch_size)
                .all()
            )

            if not pending:
                return 0

            logger.info(f"Processing {len(pending)} pending articles")

            for raw in pending:
                try:
                    raw.processing_status = "PROCESSING"
                    db.flush()

                    # Get source info for trust scoring
                    source = db.query(Source).filter(Source.id == raw.source_id).first()
                    source_reliability = self.source_scorer.score_source(source) if source else 0.5

                    # Run NLP pipeline
                    nlp_result = self.pipeline.process(
                        raw_text=raw.raw_content,
                        source_reliability=source_reliability,
                        has_author=bool(raw.author),
                    )

                    # Create processed article
                    processed = ProcessedArticle(
                        raw_article_id=raw.id,
                        source_id=raw.source_id,
                        clean_text=nlp_result.clean_text,
                        summary=nlp_result.summary,
                        language=nlp_result.language,
                        word_count=nlp_result.word_count,
                        embedding_vector=nlp_result.embedding,
                        entities_extracted=nlp_result.entities,
                        locations=nlp_result.locations,
                        sentiment_score=nlp_result.sentiment_score,
                        bias_score=nlp_result.bias_score,
                    )

                    # Trust scoring
                    if source:
                        trust = self.article_scorer.score_article(
                            processed, source, nlp_result.fake_news_result
                        )
                        processed.credibility_score = trust.score

                    db.add(processed)
                    db.flush()

                    # Event detection — assign to existing event or create new one
                    self.event_detector.detect_and_assign(processed, db)

                    raw.processing_status = "DONE"
                    processed_count += 1

                except Exception as e:
                    logger.error(f"Failed to process article {raw.id}: {e}")
                    raw.processing_status = "FAILED"
                    raw.failure_reason = str(e)[:500]

            db.commit()
            logger.info(f"Processed {processed_count}/{len(pending)} articles successfully")

        except Exception as e:
            db.rollback()
            logger.error(f"Worker batch failed: {e}")
        finally:
            db.close()

        return processed_count

    async def run_forever(self, interval: int = 30, batch_size: int = 10):
        """Continuous processing loop."""
        logger.info(f"NLP Worker started (interval: {interval}s, batch: {batch_size})")
        while True:
            try:
                count = self.process_pending(batch_size)
                if count > 0:
                    logger.info(f"Cycle: processed {count} articles")
            except Exception as e:
                logger.error(f"Worker cycle error: {e}")

            await asyncio.sleep(interval)


async def start_nlp_worker():
    """Entry point for running the NLP worker."""
    worker = NLPWorker()
    await worker.run_forever()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(start_nlp_worker())
