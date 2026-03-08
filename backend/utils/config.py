"""
Centralized configuration management using Pydantic Settings.
All environment variables and defaults are defined here.
"""

from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application-wide configuration loaded from environment variables."""

    # --- API Keys ---
    news_api_key: Optional[str] = Field(default=None, description="NewsAPI.org API key")
    serp_api_key: Optional[str] = Field(default=None, description="SerpAPI key for Google Search")

    # --- Model Configuration ---
    model_name: str = Field(default="roberta-base", description="HuggingFace model identifier")
    max_seq_length: int = Field(default=512, description="Maximum token sequence length")
    batch_size: int = Field(default=16, description="Training and inference batch size")
    learning_rate: float = Field(default=2e-5, description="Training learning rate")
    num_epochs: int = Field(default=3, description="Number of training epochs")
    num_labels: int = Field(default=2, description="Number of classification labels")

    # --- Server ---
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")
    debug: bool = Field(default=False, description="Debug mode")
    log_level: str = Field(default="INFO", description="Logging level")

    # --- Paths ---
    project_root: Path = Field(
        default_factory=lambda: Path(__file__).resolve().parent.parent.parent
    )
    model_checkpoint_dir: Path = Field(default=Path("./checkpoints"))
    data_dir: Path = Field(default=Path("./data"))
    cache_dir: Path = Field(default=Path("./cache"))

    # --- Source Credibility ---
    trusted_domains: list[str] = Field(default_factory=lambda: [
        "reuters.com", "apnews.com", "bbc.com", "bbc.co.uk",
        "nytimes.com", "washingtonpost.com", "theguardian.com",
        "nature.com", "sciencemag.org", "who.int", "cdc.gov",
        "nasa.gov", "nih.gov", "pubmed.ncbi.nlm.nih.gov",
    ])

    low_credibility_domains: list[str] = Field(default_factory=lambda: [
        "infowars.com", "naturalnews.com", "beforeitsnews.com",
        "worldnewsdailyreport.com", "theonion.com",
    ])

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


settings = Settings()
