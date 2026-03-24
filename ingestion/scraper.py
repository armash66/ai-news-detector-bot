"""Web Scraper Connector — fallback for sources without RSS/API."""

import httpx
import logging
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse
from datetime import datetime, timezone

try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False

try:
    import trafilatura
    TRAFILATURA_AVAILABLE = True
except ImportError:
    TRAFILATURA_AVAILABLE = False

from src.ingestion.base import BaseConnector, RawArticleInput

logger = logging.getLogger("truthlens.ingestion.scraper")


class ScraperConnector(BaseConnector):
    """Extracts articles from web pages using trafilatura + BeautifulSoup."""

    def __init__(self, targets: List[Dict[str, Any]] | None = None):
        super().__init__(name="scraper", source_type="SCRAPER")
        self.targets = targets or []
        self.client = httpx.AsyncClient(
            timeout=30.0,
            follow_redirects=True,
            headers={"User-Agent": "TruthLens/3.0 News Intelligence Bot"},
        )

    async def fetch(self) -> List[RawArticleInput]:
        """Scrape configured target URLs."""
        articles: List[RawArticleInput] = []

        for target in self.targets:
            try:
                result = await self._scrape_url(
                    url=target["url"],
                    source_name=target.get("name", urlparse(target["url"]).netloc),
                )
                if result:
                    articles.append(result)
            except Exception as e:
                self.logger.error(f"Scrape failed for {target.get('url')}: {e}")

        return articles

    async def _scrape_url(self, url: str, source_name: str) -> Optional[RawArticleInput]:
        """Scrape a single URL and extract article content."""
        response = await self.client.get(url)
        response.raise_for_status()
        html = response.text

        # Prefer trafilatura for content extraction (better at removing boilerplate)
        if TRAFILATURA_AVAILABLE:
            content = trafilatura.extract(html, include_comments=False) or ""
        elif BS4_AVAILABLE:
            soup = BeautifulSoup(html, "html.parser")
            # Remove scripts and styles
            for tag in soup(["script", "style", "nav", "footer", "header"]):
                tag.decompose()
            content = soup.get_text(separator=" ", strip=True)
        else:
            self.logger.error("No HTML parser available (install trafilatura or bs4)")
            return None

        # Extract title
        title = ""
        if BS4_AVAILABLE:
            soup = BeautifulSoup(html, "html.parser")
            title_tag = soup.find("title")
            if title_tag:
                title = title_tag.get_text(strip=True)

        if not content or not title:
            return None

        domain = urlparse(url).netloc

        return RawArticleInput(
            url=url,
            title=title,
            content=content[:10000],  # Cap content length
            source_domain=domain,
            source_name=source_name,
            published_at=datetime.now(timezone.utc),
            metadata={"scraper": "trafilatura" if TRAFILATURA_AVAILABLE else "bs4"},
        )

    async def health_check(self) -> bool:
        """Check if httpx client is functional."""
        try:
            response = await self.client.get("https://httpbin.org/status/200")
            return response.status_code == 200
        except Exception:
            return False

    async def close(self):
        await self.client.aclose()
