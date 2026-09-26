"""QueryWatch configuration read from Django settings."""

from __future__ import annotations

from django.conf import settings


DEFAULT_SLOW_QUERY_MS = 100.0
DEFAULT_DUPLICATE_THRESHOLD = 3
DEFAULT_MAX_QUERIES: int | None = None
DEFAULT_NPLUS1_THRESHOLD = 3


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


def max_queries() -> int | None:
    """Return the configured query-count limit, if one is configured."""
    value = getattr(settings, "QUERYWATCH_MAX_QUERIES", DEFAULT_MAX_QUERIES)
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        message = "QUERYWATCH_MAX_QUERIES must be a non-negative integer or None."
        raise ValueError(message)
    return value


def nplus1_threshold() -> int:
    """Return the configured minimum repetition count for N+1 candidates."""
    value = getattr(settings, "QUERYWATCH_NPLUS1_THRESHOLD", DEFAULT_NPLUS1_THRESHOLD)
    if isinstance(value, bool) or not isinstance(value, int) or value < 2:
        message = "QUERYWATCH_NPLUS1_THRESHOLD must be an integer of at least 2."
        raise ValueError(message)
    return value
