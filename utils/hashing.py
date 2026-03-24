"""Utility functions for content hashing and deduplication."""

import hashlib
import re
import unicodedata


def compute_content_hash(text: str) -> str:
    """Generate SHA-256 hash of normalized text for deduplication."""
    normalized = normalize_text(text)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def normalize_text(text: str) -> str:
    """Normalize text for consistent hashing — lowercase, strip whitespace, remove punctuation."""
    text = unicodedata.normalize("NFKD", text)
    text = text.lower().strip()
    text = re.sub(r"\s+", " ", text)
    return text


def compute_url_hash(url: str) -> str:
    """Hash a URL for fast lookup."""
    return hashlib.md5(url.strip().lower().encode("utf-8")).hexdigest()
