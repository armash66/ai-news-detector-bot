"""
TruthLens v3 — FastAPI Application Factory

Entry point for the API server. Registers all routers and middleware.
Run: uvicorn main:app --reload --port 8000
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from config.settings import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger("truthlens")


def create_app() -> FastAPI:
    """Build and configure the FastAPI application."""
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description="Real-Time News Detection & Intelligence Platform — Event-Centric Backend",
        version=settings.VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # CORS — allow all origins in development
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Health check
    @app.get("/health", tags=["System"])
    def health():
        return {"status": "operational", "service": settings.PROJECT_NAME, "version": settings.VERSION}

    # Register API routers
    from api.events import router as events_router
    from api.search import router as search_router
    from api.trending import router as trending_router
    from api.sources import router as sources_router
    from api.alerts import router as alerts_router
    from api.analyze import router as analyze_router
    from api.ws import router as ws_router
    from api.monitoring import router as monitoring_router

    prefix = settings.API_V1_PREFIX

    app.include_router(events_router, prefix=f"{prefix}/events", tags=["Events"])
    app.include_router(search_router, prefix=f"{prefix}/search", tags=["Search"])
    app.include_router(trending_router, prefix=f"{prefix}/trending", tags=["Trending"])
    app.include_router(sources_router, prefix=f"{prefix}/sources", tags=["Sources"])
    app.include_router(alerts_router, prefix=f"{prefix}/alerts", tags=["Alerts"])
    app.include_router(analyze_router, prefix=f"{prefix}/analyze", tags=["Analyze"])
    app.include_router(ws_router, prefix=f"{prefix}/ws", tags=["WebSocket"])
    app.include_router(monitoring_router, prefix="/admin", tags=["Monitoring"])

    # Initialize database tables
    @app.on_event("startup")
    def startup():
        from models.base import Base
        from models.database import engine
        # Import all models so they register with Base
        from models import (
            Source, RawArticle, ProcessedArticle, Event, EventArticle,
            Claim, Entity, EntityMention, TimelineEntry, Alert,
        )
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables initialized")

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
