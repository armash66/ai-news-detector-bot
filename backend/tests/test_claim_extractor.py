"""
Tests for the claim extractor module.
"""

import pytest

from backend.services.claim_extractor import ClaimExtractor


class TestClaimExtractor:
    """Tests for claim extraction."""

    def setup_method(self):
        self.extractor = ClaimExtractor()

    def test_extracts_attribution_claims(self):
        text = (
            "According to the World Health Organization, the new variant "
            "has spread to 45 countries. The CDC confirmed the findings in "
            "a press release yesterday. Local authorities said they are "
            "monitoring the situation closely."
        )
        claims = self.extractor.extract(text)
        assert len(claims) > 0
        types = [c.claim_type for c in claims]
        assert "attribution" in types

    def test_extracts_statistical_claims(self):
        text = (
            "The unemployment rate dropped to 3.5% in the last quarter. "
            "Over 2 million jobs were created in the technology sector. "
            "The GDP growth reached 4.2 percent year over year."
        )
        claims = self.extractor.extract(text)
        assert len(claims) > 0
        has_statistical = any(c.claim_type == "statistical" for c in claims)
        assert has_statistical

    def test_filters_short_sentences(self):
        text = "Short. Also short. Too brief."
        claims = self.extractor.extract(text)
        assert len(claims) == 0

    def test_filters_boilerplate(self):
        text = (
            "Subscribe to our newsletter for more updates. "
            "Click here to read more articles. "
            "Share this article on social media."
        )
        claims = self.extractor.extract(text)
        assert len(claims) == 0

    def test_max_claims_limit(self):
        text = " ".join(
            f"According to source {i}, the finding #{i} was confirmed by researchers. "
            for i in range(20)
        )
        claims = self.extractor.extract(text, max_claims=3)
        assert len(claims) <= 3

    def test_confidence_ordering(self):
        text = (
            "A study shows that 60% of participants improved their health. "
            "According to experts, the results are promising. "
            "The data reveals a significant correlation between exercise and wellness."
        )
        claims = self.extractor.extract(text)
        if len(claims) >= 2:
            confidences = [c.confidence for c in claims]
            assert confidences == sorted(confidences, reverse=True)
