"""
FastAPI application entry point.

Creates the VeritasAI API server with CORS, lifecycle management,
and route registration.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.utils.logger import get_logger

logger = get_logger("api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle manager. Initializes models on startup."""
    logger.info("VeritasAI API starting up...")

    from backend.api.dependencies import set_analyzer
    from backend.services.analyzer import ArticleAnalyzer
    from backend.database import init_db
    from backend.scrapers.news_fetcher import fetch_and_analyze_news
    from apscheduler.schedulers.asyncio import AsyncIOScheduler

    # Setup core AI
    analyzer = ArticleAnalyzer()
    set_analyzer(analyzer)
    
    # Setup Database
    logger.info("Initializing SaaS database...")
    init_db()

    # Start Background News Engine
    logger.info("Starting Background News Fetcher Scheduler...")
    scheduler = AsyncIOScheduler()
    # Trigger immediately on boot then every hour
    scheduler.add_job(fetch_and_analyze_news, 'interval', minutes=60)
    scheduler.start()
    # Kick off a manual run right now since APScheduler will wait 60 min for next
    try:
        import asyncio
        asyncio.create_task(asyncio.to_thread(fetch_and_analyze_news))
    except Exception as e:
        logger.error(f"Error starting immediate fetch: {e}")

    logger.info("All modular services loaded and ready")
    yield
    logger.info("VeritasAI API shutting down...")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="VeritasAI - Misinformation Detection Platform",
        description=(
            "Production-grade AI-powered fact-checking and misinformation detection API. "
            "Analyzes articles, verifies claims, and provides credibility reports "
            "with explainable AI insights."
        ),
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register routes (imported here to avoid circular imports)
    from backend.api.routes import analyze, verify, health, dashboard, multimodal

    app.include_router(health.router, tags=["Health"])
    app.include_router(analyze.router, prefix="/api/v1", tags=["Analysis"])
    app.include_router(verify.router, prefix="/api/v1", tags=["Verification"])
    app.include_router(multimodal.router, prefix="/api/v1", tags=["Multimodal"])
    app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["Dashboard"])

    return app


# Application instance for uvicorn
app = create_app()
