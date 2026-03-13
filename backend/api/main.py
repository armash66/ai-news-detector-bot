from fastapi import FastAPI, WebSocket, WebSocketDisconnect
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
        
    @app.websocket("/api/v1/stream/live")
    async def websocket_endpoint(websocket: WebSocket):
        from backend.api.ws_manager import manager
        await manager.connect(websocket)
        try:
            while True:
                await websocket.receive_text()
        except WebSocketDisconnect:
            manager.disconnect(websocket)
        
    # Bind Core Routers
    from backend.api.routes import analyze, feed, campaigns, narratives, sources
    app.include_router(analyze.router, prefix=f"{settings.API_V1_STR}/analyze", tags=["Intelligence Engine"])
    app.include_router(feed.router, prefix=f"{settings.API_V1_STR}/feed", tags=["Global Intel Feeds"])
    app.include_router(campaigns.router, prefix=f"{settings.API_V1_STR}/campaigns", tags=["Bot Networks"])
    app.include_router(narratives.router, prefix=f"{settings.API_V1_STR}/narratives", tags=["Narrative Analysis"])
    app.include_router(sources.router, prefix=f"{settings.API_V1_STR}/sources", tags=["Source Credibility"])
    
    # Initialize Database Tables (Phase 3)
    from backend.core.database import Base, engine
    from backend.models import domain
    Base.metadata.create_all(bind=engine)

        
    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.api.main:app", host="0.0.0.0", port=8000, reload=True)
