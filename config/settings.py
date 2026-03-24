"""
TruthLens v3 - Application Configuration

All settings are loaded from environment variables with sensible defaults.
Use .env file for local development.
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Central configuration for the TruthLens platform."""

    # ── Application ──────────────────────────────────────────────
    PROJECT_NAME: str = "TruthLens Intelligence Platform"
    VERSION: str = "3.0.0"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = False

    # ── PostgreSQL ───────────────────────────────────────────────
    POSTGRES_USER: str = "truthlens_user"
    POSTGRES_PASSWORD: str = "truthlens_password"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "truthlens"

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def ASYNC_DATABASE_URL(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    # ── SQLite Fallback (dev only) ───────────────────────────────
    USE_SQLITE: bool = True
    SQLITE_URL: str = "sqlite:///./truthlens_v3.db"

    # ── Redis ────────────────────────────────────────────────────
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None

    @property
    def REDIS_URL(self) -> str:
        auth = f":{self.REDIS_PASSWORD}@" if self.REDIS_PASSWORD else ""
        return f"redis://{auth}{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    # ── Neo4j (Knowledge Graph) ──────────────────────────────────
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "truthlens_password"

    # ── Ingestion ────────────────────────────────────────────────
    INGESTION_INTERVAL_SECONDS: int = 120
    INGESTION_MAX_ARTICLES_PER_SOURCE: int = 20
    INGESTION_MAX_RETRIES: int = 3
    INGESTION_RETRY_BACKOFF_BASE: float = 2.0

    # ── NLP Pipeline ─────────────────────────────────────────────
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384
    SPACY_MODEL: str = "en_core_web_sm"
    SUMMARIZATION_MODEL: str = "facebook/bart-large-cnn"

    # ── Event Detection ──────────────────────────────────────────
    EVENT_SIMILARITY_THRESHOLD: float = 0.78
    EVENT_MERGE_THRESHOLD: float = 0.85
    EVENT_SPLIT_SILHOUETTE_THRESHOLD: float = 0.6
    EVENT_TIME_WINDOW_HOURS: int = 72

    # ── Trust Engine ─────────────────────────────────────────────
    TRUST_SOURCE_WEIGHT: float = 0.30
    TRUST_LANGUAGE_WEIGHT: float = 0.20
    TRUST_CLAIM_WEIGHT: float = 0.20
    TRUST_CONSISTENCY_WEIGHT: float = 0.15
    TRUST_AUTHORSHIP_WEIGHT: float = 0.15

    # ── API ──────────────────────────────────────────────────────
    API_RATE_LIMIT: int = 100  # requests per minute
    API_DEFAULT_PAGE_SIZE: int = 20
    API_MAX_PAGE_SIZE: int = 100

    # ── Caching ──────────────────────────────────────────────────
    CACHE_TRENDING_TTL: int = 60
    CACHE_EVENT_TTL: int = 30
    CACHE_SEARCH_TTL: int = 120

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
