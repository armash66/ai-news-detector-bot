from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.core.config import settings
import logging

# Configure basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("truthlens.api")

def create_app() -> FastAPI:
    """Initialize TruthLens Core Gateway API"""
    app = FastAPI(
        title="TruthLens OSINT API",
        description="Global Multimodal AI Intelligence Platform",
        version="2.0.0"
    )

    # Allow frontend domains
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"], # In production, restrict this to frontend domains
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    def health_check():
        return {"status": "operational", "service": "TruthLens Gateway"}
        
    # Bind Core Routers
    from backend.api.routes import analyze, feed
    app.include_router(analyze.router, prefix=f"{settings.API_V1_STR}/analyze", tags=["Intelligence Engine"])
    app.include_router(feed.router, prefix=f"{settings.API_V1_STR}/feed", tags=["Global Intel Feeds"])
        
    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.api.main:app", host="0.0.0.0", port=8000, reload=True)
