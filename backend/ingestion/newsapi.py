"""NewsAPI Connector — ingests articles from newsapi.org."""

import httpx
import logging
from datetime import datetime, timezone
from typing import List, Optional

from ingestion.base import BaseConnector, RawArticleInput

logger = logging.getLogger("truthlens.ingestion.newsapi")

NEWSAPI_BASE_URL = "https://newsapi.org/v2"


class NewsAPIConnector(BaseConnector):
    """Fetches articles from the NewsAPI service."""

    def __init__(self, api_key: str, max_articles: int = 50):
        super().__init__(name="newsapi", source_type="API")
        self.api_key = api_key
        self.max_articles = max_articles
        self.client = httpx.AsyncClient(timeout=30.0)

    async def fetch(self, query: Optional[str] = None) -> List[RawArticleInput]:
        """Fetch top headlines or search results from NewsAPI."""
        try:
            params = {
                "apiKey": self.api_key,
                "language": "en",
                "pageSize": min(self.max_articles, 100),
            }

            if query:
                params["q"] = query
                endpoint = f"{NEWSAPI_BASE_URL}/everything"
            else:
                endpoint = f"{NEWSAPI_BASE_URL}/top-headlines"
                params["category"] = "general"
                params["country"] = "us"

            response = await self.client.get(endpoint, params=params)
            response.raise_for_status()
            data = response.json()

            if data.get("status") != "ok":
                self.logger.error(f"NewsAPI error: {data.get('message', 'Unknown')}")
                return []

            articles: List[RawArticleInput] = []
            for item in data.get("articles", []):
                if not item.get("url") or not item.get("title"):
                    continue

                published = None
                if item.get("publishedAt"):
                    try:
                        published = datetime.fromisoformat(
                            item["publishedAt"].replace("Z", "+00:00")
                        )
                    except Exception:
                        pass

                source_name = item.get("source", {}).get("name", "Unknown")
                source_domain = item.get("source", {}).get("id", source_name)

                articles.append(
                    RawArticleInput(
                        url=item["url"],
                        title=item["title"],
                        content=item.get("content") or item.get("description") or "",
                        source_domain=source_domain,
                        source_name=source_name,
                        author=item.get("author"),
                        published_at=published,
                        metadata={"image_url": item.get("urlToImage")},
                    )
                )

            self.logger.info(f"Fetched {len(articles)} articles from NewsAPI")
            return articles

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                self.logger.warning("NewsAPI rate limit hit, backing off")
            else:
                self.logger.error(f"NewsAPI HTTP error: {e}")
            return []
        except Exception as e:
            self.logger.error(f"NewsAPI fetch failed: {e}")
            return []

    async def health_check(self) -> bool:
        """Verify API key is valid."""
        try:
            response = await self.client.get(
                f"{NEWSAPI_BASE_URL}/top-headlines",
                params={"apiKey": self.api_key, "country": "us", "pageSize": 1},
            )
            return response.status_code == 200
        except Exception:
            return False

    async def close(self):
        await self.client.aclose()
