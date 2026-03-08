"""
Structured logging configuration for the platform.
"""

import logging
import sys
from functools import lru_cache


LOG_FORMAT = (
    "%(asctime)s | %(levelname)-8s | %(name)-30s | %(message)s"
)
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def _setup_root_logger(level: str = "INFO") -> None:
    """Configure the root logger for the application."""
    root_logger = logging.getLogger("veritas")
    if root_logger.handlers:
        return

    root_logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT))
    root_logger.addHandler(console_handler)


@lru_cache(maxsize=None)
def get_logger(name: str, level: str = "INFO") -> logging.Logger:
    """Get a named logger under the 'veritas' namespace.

    Args:
        name: Module or component name.
        level: Logging level string.

    Returns:
        Configured logger instance.
    """
    _setup_root_logger(level)
    return logging.getLogger(f"veritas.{name}")
