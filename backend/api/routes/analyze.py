"""
Analysis endpoints.

POST /analyze     - Analyze raw article text
POST /analyze-url - Scrape and analyze from URL
"""

from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, HttpUrl

from backend.api.dependencies import get_analyzer
from backend.utils.logger import get_logger

logger = get_logger("routes.analyze")
router = APIRouter()


# ── Request Models ──────────────────────────────────────────────────

class AnalyzeTextRequest(BaseModel):
    """Request body for text analysis."""
    text: str = Field(
        ...,
        min_length=20,
        description="Article text to analyze (minimum 20 characters)",
        examples=["NASA announced today that alien life has been confirmed in Arizona desert."],
    )
    explain: bool = Field(
        default=True,
        description="Include explainability analysis",
    )
    explanation_methods: Optional[list[str]] = Field(
        default=None,
        description="Explanation methods to use: 'attention', 'shap', 'lime'",
        examples=[["attention"]],
    )


class AnalyzeUrlRequest(BaseModel):
    """Request body for URL analysis."""
    url: str = Field(
        ...,
        description="URL of the article to analyze",
        examples=["https://www.bbc.com/news/example-article"],
    )
    explain: bool = Field(
        default=True,
        description="Include explainability analysis",
    )
    explanation_methods: Optional[list[str]] = Field(
        default=None,
        description="Explanation methods to use",
    )


# ── Endpoints ───────────────────────────────────────────────────────

@router.post("/analyze")
async def analyze_text(request: AnalyzeTextRequest):
    """Analyze article text for misinformation.

    Returns a comprehensive credibility report including:
    - Classification (REAL/FAKE with confidence)
    - Extracted claims
    - Evidence from trusted sources
    - Clickbait analysis
    - Credibility score and verdict
    - Explainability insights
    """
    try:
        analyzer = get_analyzer()
        report = analyzer.analyze_text(
            text=request.text,
            explain=request.explain,
            explanation_methods=request.explanation_methods,
        )
        return report.to_dict()
    except Exception as exc:
        logger.error("Analysis failed: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(exc)}")


@router.post("/analyze-url")
async def analyze_url(request: AnalyzeUrlRequest):
    """Scrape and analyze an article from a URL.

    First scrapes the article content, then runs the full analysis
    pipeline including source credibility assessment.
    """
    try:
        analyzer = get_analyzer()
        report = analyzer.analyze_url(
            url=request.url,
            explain=request.explain,
            explanation_methods=request.explanation_methods,
        )
        return report.to_dict()
    except Exception as exc:
        logger.error("URL analysis failed: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"URL analysis failed: {str(exc)}",
        )
