"""Analyze API Router — ad-hoc text/URL trust analysis."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import uuid

from models.database import get_db
from schemas.schemas import AnalyzeRequest, AnalyzeResponse
from nlp.pipeline import NLPPipeline
from trust.engine import ArticleScorer
from models.article import ProcessedArticle

router = APIRouter()
nlp_pipeline = NLPPipeline()
article_scorer = ArticleScorer()


@router.post("", response_model=AnalyzeResponse)
def analyze_content(
    request: AnalyzeRequest,
    db: Session = Depends(get_db)
):
    """Ad-hoc analysis of submitted text or URL for credibility."""
    if not request.text and not request.url:
        raise HTTPException(status_code=400, detail="Must provide text or url")

    text_to_analyze = request.text
    if request.url and not request.text:
        # Simple scraper fallback for ad-hoc URLs
        text_to_analyze = f"Extracted content from {request.url} would go here."

    # Run NLP pipeline synchronously for ad-hoc requests
    nlp_result = nlp_pipeline.process(
        raw_text=text_to_analyze or "",
        source_reliability=0.5,
        has_author=False
    )

    # Mock a processed article for scoring
    mock_article = ProcessedArticle(
        clean_text=nlp_result.clean_text,
        summary=nlp_result.summary,
        word_count=nlp_result.word_count,
        sentiment_score=nlp_result.sentiment_score,
        bias_score=nlp_result.bias_score,
    )

    # Score article (without a specific source)
    from models.source import Source
    unknown_source = Source(name="Unknown", domain="unknown.com", reliability_score=0.5)
    
    trust_explanation = article_scorer.score_article(
        article=mock_article,
        source=unknown_source,
        fake_news_result=nlp_result.fake_news_result
    )

    return AnalyzeResponse(
        id=str(uuid.uuid4()),
        status="DONE",
        result={
            "trust_score": trust_explanation.score,
            "breakdown": trust_explanation.breakdown,
            "sentiment": nlp_result.sentiment_score,
            "bias": nlp_result.bias_score,
            "summary": nlp_result.summary,
            "entities": [e["entity_text"] for e in nlp_result.entities[:5]],
        }
    )
