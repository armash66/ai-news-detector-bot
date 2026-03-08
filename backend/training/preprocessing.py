"""
Text preprocessing pipeline for training data.

Handles:
  - HTML removal
  - URL removal
  - Special character normalization
  - Whitespace normalization
  - Tokenizer-compatible text cleaning
"""

import re
from typing import Optional

from backend.utils.logger import get_logger

logger = get_logger("preprocessing")

# Try to import html module for entity decoding
import html as html_module


class TextPreprocessor:
    """Cleans and normalizes text for transformer input.

    Designed to be minimally invasive - transformers generally handle
    raw text well, so we only clean obvious noise (HTML, URLs, etc.).
    """

    # Compiled patterns for performance
    _HTML_TAG_RE = re.compile(r"<[^>]+>")
    _URL_RE = re.compile(r"https?://\S+|www\.\S+")
    _EMAIL_RE = re.compile(r"\S+@\S+\.\S+")
    _MULTI_SPACE_RE = re.compile(r"\s{2,}")
    _MULTI_NEWLINE_RE = re.compile(r"\n{3,}")
    _SPECIAL_CHARS_RE = re.compile(r"[^\w\s.,!?;:'\"-]")

    def clean(
        self,
        text: str,
        remove_urls: bool = True,
        remove_html: bool = True,
        remove_emails: bool = True,
        normalize_whitespace: bool = True,
        max_length: Optional[int] = None,
    ) -> str:
        """Clean a single text string.

        Args:
            text: Raw input text.
            remove_urls: Strip URLs.
            remove_html: Strip HTML tags and decode entities.
            remove_emails: Strip email addresses.
            normalize_whitespace: Collapse multiple spaces/newlines.
            max_length: Truncate to this many characters (after cleaning).

        Returns:
            Cleaned text string.
        """
        if not text or not isinstance(text, str):
            return ""

        # Decode HTML entities
        if remove_html:
            text = html_module.unescape(text)
            text = self._HTML_TAG_RE.sub(" ", text)

        if remove_urls:
            text = self._URL_RE.sub("[URL]", text)

        if remove_emails:
            text = self._EMAIL_RE.sub("[EMAIL]", text)

        if normalize_whitespace:
            text = self._MULTI_NEWLINE_RE.sub("\n\n", text)
            text = self._MULTI_SPACE_RE.sub(" ", text)
            text = text.strip()

        if max_length:
            text = text[:max_length]

        return text

    def clean_batch(
        self,
        texts: list[str],
        **kwargs,
    ) -> list[str]:
        """Clean a batch of texts.

        Args:
            texts: List of raw text strings.
            **kwargs: Passed to self.clean().

        Returns:
            List of cleaned text strings.
        """
        cleaned = [self.clean(t, **kwargs) for t in texts]
        logger.debug("Cleaned batch of %d texts", len(cleaned))
        return cleaned

    @staticmethod
    def truncate_to_sentences(
        text: str,
        max_length: int = 512,
        tokenizer=None,
    ) -> str:
        """Truncate text at sentence boundaries to fit within token limits.

        Smarter than raw truncation; avoids cutting mid-sentence.

        Args:
            text: Input text.
            max_length: Maximum token count.
            tokenizer: HuggingFace tokenizer for accurate token counting.

        Returns:
            Truncated text ending at a sentence boundary.
        """
        sentences = re.split(r'(?<=[.!?])\s+', text)
        result = []
        current_length = 0

        for sentence in sentences:
            if tokenizer:
                tokens = tokenizer.encode(sentence, add_special_tokens=False)
                sent_len = len(tokens)
            else:
                sent_len = len(sentence.split())

            if current_length + sent_len > max_length:
                break
            result.append(sentence)
            current_length += sent_len

        return " ".join(result) if result else text[:max_length * 4]
