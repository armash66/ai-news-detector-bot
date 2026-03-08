"""
Article scraper module for extracting structured content from news URLs.
Uses newspaper3k with BeautifulSoup fallback for robust extraction.
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from backend.utils.logger import get_logger

logger = get_logger("scraper")

# Try newspaper3k, fall back to manual scraping
try:
    from newspaper import Article as NewspaperArticle
    HAS_NEWSPAPER = True
except ImportError:
    HAS_NEWSPAPER = False
    logger.warning("newspaper3k not installed. Using BeautifulSoup fallback.")


@dataclass
class ScrapedArticle:
    """Structured representation of a scraped article."""
    url: str
    title: str = ""
    authors: list[str] = field(default_factory=list)
    publish_date: Optional[str] = None
    content: str = ""
    top_image: Optional[str] = None
    source_domain: str = ""
    scrape_timestamp: str = field(
        default_factory=lambda: datetime.utcnow().isoformat()
    )
    success: bool = False
    error: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)

    @property
    def word_count(self) -> int:
        return len(self.content.split()) if self.content else 0


class ArticleScraper:
    """Extracts article content from a URL.

    Uses newspaper3k as primary extractor with a BeautifulSoup fallback
    for sites that newspaper3k fails to parse.
    """

    USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
    TIMEOUT = 15

    def scrape(self, url: str) -> ScrapedArticle:
        """Scrape an article from the given URL.

        Args:
            url: Full URL of the news article.

        Returns:
            ScrapedArticle with extracted fields.
        """
        article = ScrapedArticle(url=url, source_domain=urlparse(url).netloc)

        if HAS_NEWSPAPER:
            article = self._scrape_newspaper(article)
        if not article.success or len(article.content) < 100:
            article = self._scrape_bs4(article)

        if article.content:
            article.success = True
            logger.info(
                "Scraped '%s' (%d words) from %s",
                article.title[:60],
                article.word_count,
                article.source_domain,
            )
        else:
            article.success = False
            article.error = article.error or "Failed to extract meaningful content"
            logger.warning("Scrape failed for %s: %s", url, article.error)

        return article

    # ------------------------------------------------------------------
    # Private extraction strategies
    # ------------------------------------------------------------------

    def _scrape_newspaper(self, article: ScrapedArticle) -> ScrapedArticle:
        """Primary extraction via newspaper3k."""
        try:
            np_article = NewspaperArticle(article.url)
            np_article.download()
            np_article.parse()

            article.title = np_article.title or ""
            article.authors = np_article.authors or []
            article.content = np_article.text or ""
            article.top_image = np_article.top_image
            if np_article.publish_date:
                article.publish_date = np_article.publish_date.isoformat()
            article.success = True
        except Exception as exc:
            article.error = f"newspaper3k error: {exc}"
            logger.debug(article.error)
        return article

    def _scrape_bs4(self, article: ScrapedArticle) -> ScrapedArticle:
        """Fallback extraction using BeautifulSoup."""
        try:
            headers = {"User-Agent": self.USER_AGENT}
            response = requests.get(
                article.url, headers=headers, timeout=self.TIMEOUT
            )
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            # Title
            if not article.title:
                og_title = soup.find("meta", property="og:title")
                if og_title and og_title.get("content"):
                    article.title = og_title["content"]
                elif soup.title:
                    article.title = soup.title.get_text(strip=True)

            # Authors
            if not article.authors:
                author_meta = soup.find("meta", attrs={"name": "author"})
                if author_meta and author_meta.get("content"):
                    article.authors = [author_meta["content"]]

            # Publish date
            if not article.publish_date:
                for attr in ["article:published_time", "datePublished", "date"]:
                    date_meta = soup.find("meta", attrs={"property": attr}) or \
                                soup.find("meta", attrs={"name": attr})
                    if date_meta and date_meta.get("content"):
                        article.publish_date = date_meta["content"]
                        break

            # Content: gather text from <article> or <p> tags
            content_parts: list[str] = []
            article_tag = soup.find("article")
            paragraphs = (
                article_tag.find_all("p") if article_tag
                else soup.find_all("p")
            )
            for p in paragraphs:
                text = p.get_text(strip=True)
                if len(text) > 30:
                    content_parts.append(text)

            if content_parts:
                article.content = "\n\n".join(content_parts)
                article.success = True

            # Top image
            if not article.top_image:
                og_image = soup.find("meta", property="og:image")
                if og_image and og_image.get("content"):
                    article.top_image = og_image["content"]

        except Exception as exc:
            article.error = f"BeautifulSoup error: {exc}"
            logger.debug(article.error)

        return article
