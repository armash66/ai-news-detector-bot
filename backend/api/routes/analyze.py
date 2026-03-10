"""
Analysis endpoints.

POST /analyze     - Analyze raw article text
POST /analyze-url - Scrape and analyze from URL
POST /analyze-image - Extract text from image and analyze
"""

from typing import Optional, Any

import io
import httpx
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel, Field, HttpUrl
from PIL import Image
import pytesseract

from backend.api.dependencies import get_analyzer
from backend.services.analyzer import ArticleAnalyzer
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


# ── Response Models ─────────────────────────────────────────────────

class AnalysisResponse(BaseModel):
    """Standard response model for analysis endpoints."""
    input_text: Optional[str] = Field(
        None,
        description="The text that was analyzed (if applicable)",
    )
    input_url: Optional[HttpUrl] = Field(
        None,
        description="The URL that was analyzed (if applicable)",
    )
    article: Optional[dict] = Field(
        None,
        description="Scraped article content (if applicable)",
    )
    classification: Optional[dict] = Field(
        None,
        description="Classification results (e.g., REAL/FAKE, confidence)",
    )
    claims: Optional[list] = Field(
        None,
        description="Extracted claims from the text",
    )
    evidence: Optional[list] = Field(
        None,
        description="Evidence found for/against claims",
    )
    clickbait: Optional[dict] = Field(
        None,
        description="Clickbait analysis results",
    )
    credibility: Optional[dict] = Field(
        None,
        description="Overall credibility score and verdict",
    )
    explanations: Optional[dict] = Field(
        None,
        description="Explainability insights (e.g., attention weights, SHAP values)",
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


@router.post("/analyze-image", response_model=AnalysisResponse)
async def analyze_image(
    file: UploadFile = File(...),
    explain: bool = False,
    analyzer: ArticleAnalyzer = Depends(get_analyzer)
):
    """
    Extracts text from an uploaded image using OCR and analyzes it for misinformation.
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Uploaded file must be an image.")

    try:
        image_bytes = await file.read()
        image = Image.open(io.BytesIO(image_bytes))

        # Extract Text
        extracted_text = pytesseract.image_to_string(image)
        if len(extracted_text.strip()) < 20:
            raise HTTPException(
                status_code=400,
                detail="Not enough readable text found in the image. Requires at least 20 characters."
            )

        logger.info(f"OCR Extracted {len(extracted_text)} chars from image. Analyzing...")

        # Pass to standard pipeline
        report = analyzer.analyze_text(extracted_text, explain=explain) # Changed to analyze_text as per existing analyzer methods

        return AnalysisResponse(
            input_text=extracted_text,  # Show the user what was extracted
            input_url=None,
            article=None,
            classification=report.classification,
            claims=report.claims,
            evidence=report.evidence,
            clickbait=report.clickbait,
            credibility=report.credibility,
            explanations=report.explanations
        )

    except httpx.HTTPError as e:
         raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Image analysis failed: {str(e)}", exc_info=True)
        if "tesseract is not installed" in str(e).lower():
            raise HTTPException(status_code=500, detail="Tesseract OCR engine is not installed on the host OS.")
        raise HTTPException(status_code=500, detail="Internal server error during analysis")


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
