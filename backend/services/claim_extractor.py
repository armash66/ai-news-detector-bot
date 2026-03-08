"""
Claim extraction pipeline.

Extracts verifiable factual claims from article text using NLP
sentence segmentation and heuristic filtering.

Pipeline: Article -> Sentence segmentation -> Claim filtering -> Structured claims
"""

import re
from dataclasses import dataclass, field
from typing import Optional

from backend.utils.logger import get_logger

logger = get_logger("claim_extractor")

# Attempt to load spaCy; fall back to regex-based segmentation
try:
    import spacy
    try:
        nlp = spacy.load("en_core_web_sm")
    except OSError:
        nlp = None
        logger.warning(
            "spaCy model 'en_core_web_sm' not found. "
            "Install with: python -m spacy download en_core_web_sm"
        )
    HAS_SPACY = nlp is not None
except Exception:
    HAS_SPACY = False
    nlp = None
    logger.warning("spaCy unavailable. Using regex-based sentence segmentation.")


@dataclass
class ExtractedClaim:
    """A single extracted factual claim."""
    text: str
    claim_type: str  # "factual", "statistical", "attribution", "causal"
    confidence: float  # 0-1 heuristic confidence
    source_sentence: str = ""
    entities: list[str] = field(default_factory=list)


# ------------------------------------------------------------------ #
# Patterns that indicate a sentence contains a verifiable claim
# ------------------------------------------------------------------ #
CLAIM_INDICATORS = [
    (r"\b(?:according to|said|stated|reported|confirmed|announced|claimed)\b", "attribution", 0.8),
    (r"\b\d+(?:\.\d+)?%?\s*(?:of|percent|million|billion|thousand|increase|decrease)\b", "statistical", 0.85),
    (r"\b(?:study|research|report|survey|data|evidence)\s+(?:shows?|found|reveals?|suggests?|indicates?)\b", "factual", 0.9),
    (r"\b(?:caused?|leads? to|results? in|linked to|associated with)\b", "causal", 0.7),
    (r"\b(?:is|are|was|were|has been|have been)\s+(?:the (?:first|largest|smallest|most|least|only))\b", "factual", 0.75),
    (r"\b(?:proven|disproven|debunked|verified|fact-checked)\b", "factual", 0.85),
    (r"\b(?:will|shall|is going to|plans? to|expected to|projected to)\b", "factual", 0.6),
]

# Patterns that disqualify a sentence from being a claim
DISQUALIFIERS = [
    r"^\s*(?:share|subscribe|follow|click|sign up|comment)",
    r"(?:read more|continue reading|related articles|advertisement)",
    r"^\s*(?:photo|image|video|credit|source|getty|shutterstock|ap photo)",
    r"^\s*\w{1,3}\s*$",  # Very short fragments
]


class ClaimExtractor:
    """Extracts verifiable factual claims from article text.

    Uses spaCy for sentence segmentation when available, with a regex
    fallback. Each sentence is scored against claim indicator patterns
    and filtered for quality.
    """

    MIN_SENTENCE_LENGTH = 30
    MAX_CLAIMS = 10

    def extract(self, text: str, max_claims: Optional[int] = None) -> list[ExtractedClaim]:
        """Extract factual claims from article text.

        Args:
            text: Article body text.
            max_claims: Maximum number of claims to return.

        Returns:
            List of ExtractedClaim objects sorted by confidence (desc).
        """
        max_claims = max_claims or self.MAX_CLAIMS
        sentences = self._segment_sentences(text)
        logger.debug("Segmented %d sentences from text", len(sentences))

        claims: list[ExtractedClaim] = []
        for sentence in sentences:
            clean = sentence.strip()
            if len(clean) < self.MIN_SENTENCE_LENGTH:
                continue
            if self._is_disqualified(clean):
                continue

            claim = self._score_sentence(clean)
            if claim:
                claims.append(claim)

        # Sort by confidence and limit
        claims.sort(key=lambda c: c.confidence, reverse=True)
        result = claims[:max_claims]
        logger.info("Extracted %d claims from %d sentences", len(result), len(sentences))
        return result

    # ------------------------------------------------------------------
    # Internal methods
    # ------------------------------------------------------------------

    @staticmethod
    def _segment_sentences(text: str) -> list[str]:
        """Split text into sentences."""
        if HAS_SPACY and nlp is not None:
            doc = nlp(text[:100_000])  # Limit for performance
            return [sent.text.strip() for sent in doc.sents]
        # Regex fallback
        sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', text)
        return [s.strip() for s in sentences if s.strip()]

    @staticmethod
    def _is_disqualified(sentence: str) -> bool:
        """Check if a sentence is boilerplate / non-claim."""
        for pattern in DISQUALIFIERS:
            if re.search(pattern, sentence, re.IGNORECASE):
                return True
        return False

    def _score_sentence(self, sentence: str) -> Optional[ExtractedClaim]:
        """Score a sentence against claim indicators."""
        best_type = "factual"
        best_confidence = 0.0

        for pattern, claim_type, weight in CLAIM_INDICATORS:
            if re.search(pattern, sentence, re.IGNORECASE):
                if weight > best_confidence:
                    best_confidence = weight
                    best_type = claim_type

        if best_confidence < 0.5:
            return None

        entities = self._extract_entities(sentence)

        return ExtractedClaim(
            text=sentence,
            claim_type=best_type,
            confidence=round(best_confidence, 2),
            source_sentence=sentence,
            entities=entities,
        )

    @staticmethod
    def _extract_entities(sentence: str) -> list[str]:
        """Extract named entities from a sentence."""
        if HAS_SPACY and nlp is not None:
            doc = nlp(sentence)
            return list({ent.text for ent in doc.ents})
        # Fallback: extract capitalized multi-word phrases
        pattern = r'\b(?:[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b'
        matches = re.findall(pattern, sentence)
        return list(set(matches))[:5]
