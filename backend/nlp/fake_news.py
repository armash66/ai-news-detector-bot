"""Fake News Classifier — scores article reliability (sub-feature of trust engine)."""

import logging
import re
from typing import Dict, Any, List

logger = logging.getLogger("truthlens.nlp.fake_news")


class FakeNewsClassifier:
    """
    Classifies article reliability using linguistic features and source scoring.
    
    This is a SUB-FEATURE — not the primary focus of TruthLens.
    Labels are always probabilistic with explainability.
    """

    # Linguistic red flags
    CLICKBAIT_PATTERNS = [
        r"(?i)you won'?t believe",
        r"(?i)what happened next",
        r"(?i)doctors hate",
        r"(?i)one weird trick",
        r"(?i)shocking truth about",
        r"(?i)\d+ reasons why",
        r"(?i)exposed!?",
    ]

    PROPAGANDA_MARKERS = [
        "wake up", "mainstream media", "they don't want you to know",
        "deep state", "fake news", "plandemic", "sheeple",
        "big pharma", "new world order", "controlled opposition",
    ]

    def classify(
        self,
        text: str,
        source_reliability: float = 0.5,
        has_author: bool = True,
    ) -> Dict[str, Any]:
        """
        Classify an article's reliability.
        
        Returns:
            {label, confidence, reasons: [str]}
            Label is RELIABLE or LOW_CREDIBILITY (never "FAKE NEWS").
        """
        reasons: List[str] = []
        score = 0.5  # Start neutral

        # Factor 1: Source reliability (weight: 0.3)
        source_component = source_reliability * 0.3
        score += source_component - 0.15  # Center around 0

        # Factor 2: Clickbait detection (weight: 0.15)
        clickbait_count = sum(1 for p in self.CLICKBAIT_PATTERNS if re.search(p, text))
        if clickbait_count > 0:
            score -= clickbait_count * 0.05
            reasons.append(f"Contains {clickbait_count} clickbait pattern(s)")

        # Factor 3: Propaganda markers (weight: 0.2)
        text_lower = text.lower()
        propaganda_count = sum(1 for m in self.PROPAGANDA_MARKERS if m in text_lower)
        if propaganda_count > 0:
            score -= propaganda_count * 0.06
            reasons.append(f"Contains {propaganda_count} propaganda-associated phrase(s)")

        # Factor 4: Authorship (weight: 0.1)
        if not has_author:
            score -= 0.05
            reasons.append("No author attribution")

        # Factor 5: Excessive caps/exclamation (weight: 0.1)
        caps_ratio = sum(1 for c in text if c.isupper()) / max(len(text), 1)
        exclamation_count = text.count("!")
        if caps_ratio > 0.15:
            score -= 0.05
            reasons.append("Excessive capitalization")
        if exclamation_count > 3:
            score -= 0.03
            reasons.append("Excessive exclamation marks")

        # Factor 6: Text quality (word count, sentence length)
        words = text.split()
        if len(words) < 50:
            score -= 0.05
            reasons.append("Very short article")

        # Clamp score
        score = max(0.0, min(1.0, score))

        if not reasons:
            reasons.append("No significant reliability concerns detected")

        label = "RELIABLE" if score >= 0.5 else "LOW_CREDIBILITY"

        return {
            "label": label,
            "confidence": round(abs(score - 0.5) * 2, 3),  # 0-1 confidence
            "reliability_score": round(score, 3),
            "reasons": reasons,
        }
