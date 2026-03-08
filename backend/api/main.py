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

    analyzer = ArticleAnalyzer()
    set_analyzer(analyzer)
    logger.info("All models loaded and ready")
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
    from backend.api.routes import analyze, verify, health

    app.include_router(health.router, tags=["Health"])
    app.include_router(analyze.router, prefix="/api/v1", tags=["Analysis"])
    app.include_router(verify.router, prefix="/api/v1", tags=["Verification"])

    return app


# Application instance for uvicorn
app = create_app()
