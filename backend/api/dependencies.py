"""
Shared dependencies for API routes.
Holds the global analyzer instance to avoid circular imports.
"""

from typing import Optional

from backend.services.analyzer import ArticleAnalyzer
from backend.utils.logger import get_logger

logger = get_logger("api.deps")

_analyzer: Optional[ArticleAnalyzer] = None


def get_analyzer() -> ArticleAnalyzer:
    """Get or create the global ArticleAnalyzer instance."""
    global _analyzer
    if _analyzer is None:
        logger.info("Initializing ArticleAnalyzer on first request...")
        _analyzer = ArticleAnalyzer()
    return _analyzer


def set_analyzer(analyzer: ArticleAnalyzer) -> None:
    """Set the global analyzer (used during app startup)."""
    global _analyzer
    _analyzer = analyzer
