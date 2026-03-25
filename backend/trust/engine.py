"""Trust Engine — source scoring, article scoring, contradiction detection, explainability."""

import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from sqlalchemy.orm import Session

from models.source import Source
from models.article import ProcessedArticle
from models.event import Event, EventArticle
from config.settings import settings

logger = logging.getLogger("truthlens.trust")


@dataclass
class TrustExplanation:
    """Human-readable breakdown of a trust score."""
    score: float
    breakdown: Dict[str, Dict[str, Any]]


class SourceScorer:
    """Scores source credibility based on multiple factors."""

    # Known reliable sources (baseline scores)
    KNOWN_SOURCES = {
        "bbc.co.uk": {"score": 0.92, "bias": "CENTER"},
        "reuters.com": {"score": 0.95, "bias": "CENTER"},
        "apnews.com": {"score": 0.95, "bias": "CENTER"},
        "nytimes.com": {"score": 0.88, "bias": "CENTER_LEFT"},
        "theguardian.com": {"score": 0.85, "bias": "CENTER_LEFT"},
        "washingtonpost.com": {"score": 0.87, "bias": "CENTER_LEFT"},
        "cnn.com": {"score": 0.78, "bias": "CENTER_LEFT"},
        "foxnews.com": {"score": 0.70, "bias": "RIGHT"},
        "aljazeera.com": {"score": 0.80, "bias": "CENTER"},
        "timesofindia.indiatimes.com": {"score": 0.72, "bias": "CENTER"},
    }

    def score_source(self, source: Source) -> float:
        """Compute credibility score for a source."""
        domain = source.domain.lower()

        # Check known sources first
        for known_domain, info in self.KNOWN_SOURCES.items():
            if known_domain in domain:
                return info["score"]

        # Default scoring based on attributes
        score = 0.5  # Start neutral

        if source.is_verified:
            score += 0.15

        # Existing reliability if set
        if source.reliability_score and source.reliability_score != 0.5:
            score = source.reliability_score

        return max(0.0, min(1.0, score))

    def get_bias_rating(self, source: Source) -> str:
        """Get bias rating for a source."""
        domain = source.domain.lower()
        for known_domain, info in self.KNOWN_SOURCES.items():
            if known_domain in domain:
                return info["bias"]
        return source.bias_rating or "UNKNOWN"


class ArticleScorer:
    """Scores individual articles based on source + content analysis."""

    def __init__(self):
        self.source_scorer = SourceScorer()

    def score_article(
        self,
        article: ProcessedArticle,
        source: Source,
        fake_news_result: Optional[Dict[str, Any]] = None,
    ) -> TrustExplanation:
        """
        Compute trust score for an article with full explainability.
        
        Returns TrustExplanation with score and human-readable breakdown.
        """
        breakdown = {}

        # Factor 1: Source reliability (weight: 0.30)
        source_score = self.source_scorer.score_source(source)
        breakdown["source_reliability"] = {
            "value": source_score,
            "weight": settings.TRUST_SOURCE_WEIGHT,
            "reason": f"{source.name}: {'verified' if source.is_verified else 'unverified'} source",
        }

        # Factor 2: Language quality (weight: 0.20)
        language_score = self._assess_language_quality(article)
        breakdown["language_quality"] = {
            "value": language_score,
            "weight": settings.TRUST_LANGUAGE_WEIGHT,
            "reason": self._language_reason(language_score),
        }

        # Factor 3: Claim verification (weight: 0.20)
        claim_score = 0.5  # Neutral if no fake news result
        if fake_news_result:
            claim_score = fake_news_result.get("reliability_score", 0.5)
        breakdown["content_analysis"] = {
            "value": claim_score,
            "weight": settings.TRUST_CLAIM_WEIGHT,
            "reason": fake_news_result.get("reasons", ["No analysis"])[0] if fake_news_result else "Not analyzed",
        }

        # Factor 4: Authorship (weight: 0.15)
        authorship_score = 0.7 if article.raw_article_id else 0.3
        breakdown["authorship"] = {
            "value": authorship_score,
            "weight": settings.TRUST_AUTHORSHIP_WEIGHT,
            "reason": "Author attributed" if authorship_score > 0.5 else "No author attribution",
        }

        # Factor 5: Consistency (weight: 0.15) — placeholder
        consistency_score = 0.5
        breakdown["consistency"] = {
            "value": consistency_score,
            "weight": settings.TRUST_CONSISTENCY_WEIGHT,
            "reason": "Consistency check pending",
        }

        # Weighted sum
        total = sum(
            info["value"] * info["weight"]
            for info in breakdown.values()
        )

        return TrustExplanation(score=round(total, 3), breakdown=breakdown)

    def _assess_language_quality(self, article: ProcessedArticle) -> float:
        """Score language quality based on bias indicators."""
        score = 0.8  # Start high

        if article.bias_score and article.bias_score > 0.3:
            score -= article.bias_score * 0.3

        if article.word_count and article.word_count < 100:
            score -= 0.1  # Very short articles are less reliable

        return max(0.0, min(1.0, score))

    def _language_reason(self, score: float) -> str:
        if score >= 0.8:
            return "Professional, neutral language"
        elif score >= 0.6:
            return "Some emotional or biased language detected"
        else:
            return "Significant sensational or biased language"


class ContradictionDetector:
    """Detects contradictions between articles covering the same event."""

    def find_contradictions(
        self,
        event_id: str,
        db: Session,
    ) -> List[Dict[str, Any]]:
        """
        Identify potential contradictions among articles in the same event.
        
        Uses simple heuristic: articles with opposing sentiment scores
        and different sources are flagged for review.
        """
        articles = (
            db.query(ProcessedArticle)
            .join(EventArticle, EventArticle.article_id == ProcessedArticle.id)
            .filter(EventArticle.event_id == event_id)
            .filter(ProcessedArticle.sentiment_score.isnot(None))
            .all()
        )

        if len(articles) < 2:
            return []

        contradictions = []
        for i, art_a in enumerate(articles):
            for art_b in articles[i + 1:]:
                # Different sources + opposing sentiment = potential contradiction
                if art_a.source_id != art_b.source_id:
                    if art_a.sentiment_score and art_b.sentiment_score:
                        sentiment_diff = abs(art_a.sentiment_score - art_b.sentiment_score)
                        if sentiment_diff > 1.0:  # Significant sentiment divergence
                            contradictions.append({
                                "article_a_id": art_a.id,
                                "article_b_id": art_b.id,
                                "sentiment_divergence": round(sentiment_diff, 3),
                                "description": (
                                    f"Sentiment divergence ({sentiment_diff:.2f}) between "
                                    f"articles from different sources"
                                ),
                            })

        return contradictions
