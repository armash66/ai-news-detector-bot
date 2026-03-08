"""
Tests for the clickbait detector and credibility scorer.
"""

import pytest

from backend.models.clickbait import ClickbaitDetector
from backend.models.credibility import CredibilityScorer


class TestClickbaitDetector:
    """Tests for clickbait detection."""

    def setup_method(self):
        self.detector = ClickbaitDetector()

    def test_detects_obvious_clickbait(self):
        headline = "You Won't BELIEVE What This Doctor Found!! SHOCKING!!"
        result = self.detector.analyze(headline)
        assert result.is_clickbait is True
        assert result.score > 0.5
        assert len(result.flags) > 0

    def test_passes_legitimate_headline(self):
        headline = "Federal Reserve Holds Interest Rates Steady Amid Economic Uncertainty"
        result = self.detector.analyze(headline)
        assert result.is_clickbait is False
        assert result.score < 0.35

    def test_detects_listicle_pattern(self):
        headline = "10 Reasons Why You Should Never Eat Bananas Again"
        result = self.detector.analyze(headline)
        assert result.score > 0.0
        assert any("Listicle" in f for f in result.flags)

    def test_detects_excessive_caps(self):
        headline = "THIS IS ALL IN CAPS AND VERY IMPORTANT"
        result = self.detector.analyze(headline)
        assert any("capitalization" in f.lower() for f in result.flags)

    def test_score_capped_at_one(self):
        headline = (
            "You Won't BELIEVE These SHOCKING 10 Secrets Doctors "
            "Don't Want You To Know!! INSANE!! JAW-DROPPING!!"
        )
        result = self.detector.analyze(headline)
        assert result.score <= 1.0


class TestCredibilityScorer:
    """Tests for credibility scoring."""

    def setup_method(self):
        self.scorer = CredibilityScorer()

    def test_high_credibility(self):
        report = self.scorer.score(
            model_confidence_real=0.92,
            source_domain="reuters.com",
            evidence_found=5,
            evidence_supporting=4,
            clickbait_score=0.05,
            text="A well-written factual article about economic policy.",
        )
        assert report.credibility_score > 70
        assert "Credible" in report.verdict

    def test_low_credibility(self):
        report = self.scorer.score(
            model_confidence_real=0.15,
            source_domain="infowars.com",
            evidence_found=0,
            evidence_supporting=0,
            clickbait_score=0.8,
            text="They don't want you to know the truth! Big pharma exposed!",
        )
        assert report.credibility_score < 40
        assert "Misinformation" in report.verdict

    def test_unknown_source(self):
        report = self.scorer.score(
            model_confidence_real=0.6,
            source_domain="random-unknown-blog.xyz",
            evidence_found=2,
            evidence_supporting=1,
            clickbait_score=0.2,
        )
        # Unknown source should get neutral score
        assert 30 < report.credibility_score < 80

    def test_reasons_populated(self):
        report = self.scorer.score(
            model_confidence_real=0.3,
            source_domain="",
            evidence_found=0,
            evidence_supporting=0,
            clickbait_score=0.6,
        )
        assert len(report.reasons) > 0

    def test_component_scores_present(self):
        report = self.scorer.score(
            model_confidence_real=0.7,
            source_domain="bbc.com",
            evidence_found=3,
            evidence_supporting=2,
            clickbait_score=0.1,
        )
        assert "model_prediction" in report.component_scores
        assert "source_credibility" in report.component_scores
        assert "evidence_support" in report.component_scores
        assert "clickbait" in report.component_scores
        assert "language_patterns" in report.component_scores
