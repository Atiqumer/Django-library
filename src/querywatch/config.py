"""QueryWatch configuration read from Django settings."""

from __future__ import annotations

from django.conf import settings


DEFAULT_SLOW_QUERY_MS = 100.0


def slow_query_threshold_ms() -> float:
    """Return the configured slow-query threshold in milliseconds."""
    value = getattr(settings, "QUERYWATCH_SLOW_QUERY_MS", DEFAULT_SLOW_QUERY_MS)
    if isinstance(value, bool) or not isinstance(value, int | float) or value < 0:
        message = "QUERYWATCH_SLOW_QUERY_MS must be a non-negative number."
        raise ValueError(message)
    return float(value)
