"""Base connector interface — all ingestion connectors implement this."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime
import logging


logger = logging.getLogger("truthlens.ingestion")


@dataclass
class RawArticleInput:
    """Standardized article structure from any connector."""
    url: str
    title: str
    content: str
    source_domain: str
    source_name: str
    author: str | None = None
    published_at: datetime | None = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class BaseConnector(ABC):
    """Abstract base for all news source connectors."""

    def __init__(self, name: str, source_type: str):
        self.name = name
        self.source_type = source_type
        self.logger = logging.getLogger(f"truthlens.ingestion.{name}")

    @abstractmethod
    async def fetch(self) -> List[RawArticleInput]:
        """Fetch latest articles from this source. Returns standardized articles."""
        ...

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the source is reachable."""
        ...

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name={self.name}>"
