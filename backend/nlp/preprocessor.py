"""Text Preprocessor — cleans and normalizes raw article text for NLP."""

import re
import logging
from dataclasses import dataclass

logger = logging.getLogger("truthlens.nlp.preprocessor")

try:
    from langdetect import detect as detect_language
    LANGDETECT_AVAILABLE = True
except ImportError:
    LANGDETECT_AVAILABLE = False


@dataclass
class CleanedText:
    text: str
    language: str
    word_count: int
    sentence_count: int


class TextPreprocessor:
    """Cleans raw article text: strips HTML, normalizes whitespace, detects language."""

    # Common boilerplate patterns to remove
    BOILERPLATE_PATTERNS = [
        r"(?i)subscribe to our newsletter.*",
        r"(?i)follow us on (twitter|facebook|instagram).*",
        r"(?i)share this article.*",
        r"(?i)read more:.*",
        r"(?i)advertisement.*",
        r"(?i)cookie policy.*",
        r"(?i)copyright \d{4}.*",
        r"(?i)all rights reserved.*",
    ]

    def clean(self, raw_text: str) -> CleanedText:
        """Full cleaning pipeline."""
        if not raw_text or not raw_text.strip():
            return CleanedText(text="", language="unknown", word_count=0, sentence_count=0)

        text = raw_text

        # Step 1: Remove HTML tags
        text = re.sub(r"<[^>]+>", " ", text)

        # Step 2: Remove HTML entities
        text = re.sub(r"&[a-zA-Z]+;", " ", text)
        text = re.sub(r"&#\d+;", " ", text)

        # Step 3: Remove URLs
        text = re.sub(r"https?://\S+", "", text)

        # Step 4: Remove boilerplate
        for pattern in self.BOILERPLATE_PATTERNS:
            text = re.sub(pattern, "", text)

        # Step 5: Normalize whitespace
        text = re.sub(r"\s+", " ", text).strip()

        # Step 6: Remove very short junk lines
        lines = text.split(". ")
        lines = [l for l in lines if len(l.split()) > 3]
        text = ". ".join(lines)

        # Detect language
        language = "en"
        if LANGDETECT_AVAILABLE and len(text) > 50:
            try:
                language = detect_language(text)
            except Exception:
                language = "en"

        words = text.split()
        sentences = [s for s in re.split(r'[.!?]+', text) if s.strip()]

        return CleanedText(
            text=text,
            language=language,
            word_count=len(words),
            sentence_count=len(sentences),
        )
