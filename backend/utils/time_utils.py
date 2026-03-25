"""Time utility functions."""

from datetime import datetime, timezone, timedelta


def utc_now() -> datetime:
    """Get current UTC timestamp."""
    return datetime.now(timezone.utc)


def hours_ago(hours: int) -> datetime:
    """Get UTC timestamp N hours ago."""
    return datetime.now(timezone.utc) - timedelta(hours=hours)


def is_within_window(dt: datetime, window_hours: int) -> bool:
    """Check if a datetime is within the last N hours."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt > hours_ago(window_hours)
