"""
Health check endpoint.
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check():
    """Basic health check."""
    return {
        "status": "up",
        "service": "News Intelligence Misinformation Detection Platform",
        "environment": "production",
    }


@router.get("/")
async def root():
    """API root with service info."""
    return {
        "service": "VeritasAI",
        "description": "AI-powered misinformation detection platform",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "analyze_text": "POST /api/v1/analyze",
            "analyze_url": "POST /api/v1/analyze-url",
            "verify_claim": "POST /api/v1/verify-claim",
            "health": "GET /health",
        },
    }
