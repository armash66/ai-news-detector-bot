"""Sentiment & Bias Analyzer — scores article sentiment and framing bias."""

import logging
from typing import Dict
from dataclasses import dataclass

logger = logging.getLogger("truthlens.nlp.sentiment")

# Lazy-loaded model
_sentiment_model = None


@dataclass
class SentimentResult:
    positive: float
    negative: float
    neutral: float
    compound: float  # -1.0 to 1.0


class SentimentAnalyzer:
    """Analyzes sentiment and bias using transformer models with heuristic fallback."""

    # Emotional language indicators for bias scoring
    BIAS_INDICATORS = {
        "left": ["progressive", "equality", "marginalized", "systemic", "social justice"],
        "right": ["patriot", "freedom", "traditional", "illegal immigration", "radical"],
        "sensational": ["shocking", "breaking", "explosive", "devastating", "outrage",
                        "slammed", "destroyed", "blasted", "horrific", "unbelievable"],
    }

    def analyze(self, text: str) -> SentimentResult:
        """Analyze sentiment of text. Uses transformer if available, falls back to heuristic."""
        if not text:
            return SentimentResult(positive=0.33, negative=0.33, neutral=0.34, compound=0.0)

        try:
            return self._transformer_sentiment(text)
        except Exception:
            return self._heuristic_sentiment(text)

    def _transformer_sentiment(self, text: str) -> SentimentResult:
        """Use HuggingFace pipeline for sentiment analysis."""
        global _sentiment_model
        if _sentiment_model is None:
            from transformers import pipeline
            _sentiment_model = pipeline(
                "sentiment-analysis",
                model="distilbert-base-uncased-finetuned-sst-2-english",
                truncation=True,
                max_length=512,
            )

        # Truncate text
        words = text.split()[:400]
        truncated = " ".join(words)
        result = _sentiment_model(truncated)[0]

        label = result["label"]
        score = result["score"]

        if label == "POSITIVE":
            return SentimentResult(
                positive=score, negative=1 - score, neutral=0.0,
                compound=score * 2 - 1,
            )
        else:
            return SentimentResult(
                positive=1 - score, negative=score, neutral=0.0,
                compound=-(score * 2 - 1),
            )

    def _heuristic_sentiment(self, text: str) -> SentimentResult:
        """Simple word-count heuristic fallback."""
        positive_words = {"good", "great", "success", "positive", "improve", "growth", "peace", "achieve"}
        negative_words = {"bad", "fail", "crisis", "attack", "death", "war", "conflict", "threat", "kill"}

        words = set(text.lower().split())
        pos_count = len(words & positive_words)
        neg_count = len(words & negative_words)
        total = max(pos_count + neg_count, 1)

        return SentimentResult(
            positive=pos_count / total,
            negative=neg_count / total,
            neutral=1 - (pos_count + neg_count) / max(len(words), 1),
            compound=(pos_count - neg_count) / total,
        )

    def compute_bias_score(self, text: str) -> float:
        """Compute a 0-1 bias score based on presence of loaded language."""
        text_lower = text.lower()
        sensational_hits = sum(1 for word in self.BIAS_INDICATORS["sensational"] if word in text_lower)
        total_words = max(len(text.split()), 1)
        return min(1.0, sensational_hits / (total_words * 0.01 + 1))
