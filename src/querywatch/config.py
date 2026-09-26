"""QueryWatch configuration read from Django settings."""

from __future__ import annotations

from django.conf import settings


DEFAULT_SLOW_QUERY_MS = 100.0
DEFAULT_DUPLICATE_THRESHOLD = 3


def slow_query_threshold_ms() -> float:
    """Return the configured slow-query threshold in milliseconds."""
    value = getattr(settings, "QUERYWATCH_SLOW_QUERY_MS", DEFAULT_SLOW_QUERY_MS)
    if isinstance(value, bool) or not isinstance(value, int | float) or value < 0:
        message = "QUERYWATCH_SLOW_QUERY_MS must be a non-negative number."
        raise ValueError(message)
    return float(value)


def duplicate_query_threshold() -> int:
    """Return the configured minimum execution count for duplicates."""
    value = getattr(
        settings, "QUERYWATCH_DUPLICATE_THRESHOLD", DEFAULT_DUPLICATE_THRESHOLD
    )
    if isinstance(value, bool) or not isinstance(value, int) or value < 2:
        message = "QUERYWATCH_DUPLICATE_THRESHOLD must be an integer of at least 2."
        raise ValueError(message)
    return value
