"""Ingestion Worker — entry point for the ingestion scheduler."""

import asyncio
import logging

from src.ingestion.scheduler import IngestionScheduler

logger = logging.getLogger("truthlens.workers.ingestion")


async def start_ingestion_worker():
    """Entry point for running the ingestion scheduler."""
    scheduler = IngestionScheduler()
    await scheduler.run_forever()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(start_ingestion_worker())
