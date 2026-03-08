"""
Tests for the article scraper module.
"""

import pytest
from unittest.mock import patch, MagicMock

from backend.scrapers.article_scraper import ArticleScraper, ScrapedArticle


class TestScrapedArticle:
    """Tests for the ScrapedArticle dataclass."""

    def test_default_values(self):
        article = ScrapedArticle(url="https://example.com")
        assert article.url == "https://example.com"
        assert article.title == ""
        assert article.content == ""
        assert article.success is False
        assert article.word_count == 0

    def test_word_count(self):
        article = ScrapedArticle(url="https://example.com", content="hello world foo bar")
        assert article.word_count == 4

    def test_to_dict(self):
        article = ScrapedArticle(url="https://example.com", title="Test")
        d = article.to_dict()
        assert isinstance(d, dict)
        assert d["url"] == "https://example.com"
        assert d["title"] == "Test"


class TestArticleScraper:
    """Tests for the ArticleScraper."""

    def test_scrape_returns_scraped_article(self):
        scraper = ArticleScraper()
        with patch.object(scraper, '_scrape_newspaper') as mock_np, \
             patch.object(scraper, '_scrape_bs4') as mock_bs4:

            mock_np.return_value = ScrapedArticle(
                url="https://example.com",
                title="Test Article",
                content="This is a test article with enough content to pass the check. " * 5,
                success=True,
            )
            mock_bs4.return_value = mock_np.return_value

            result = scraper.scrape("https://example.com")
            assert result.success is True
            assert result.title == "Test Article"

    def test_fallback_to_bs4_on_short_content(self):
        scraper = ArticleScraper()
        short_article = ScrapedArticle(
            url="https://example.com",
            content="Short",
            success=True,
        )
        full_article = ScrapedArticle(
            url="https://example.com",
            content="Full article content " * 20,
            success=True,
            title="Full Article",
        )

        with patch.object(scraper, '_scrape_newspaper', return_value=short_article), \
             patch.object(scraper, '_scrape_bs4', return_value=full_article):
            result = scraper.scrape("https://example.com")
            assert result.word_count > 10

    def test_failed_scrape(self):
        scraper = ArticleScraper()
        failed = ScrapedArticle(
            url="https://example.com",
            success=False,
            error="Connection failed",
        )

        with patch.object(scraper, '_scrape_newspaper', return_value=failed), \
             patch.object(scraper, '_scrape_bs4', return_value=failed):
            result = scraper.scrape("https://example.com")
            assert result.success is False
