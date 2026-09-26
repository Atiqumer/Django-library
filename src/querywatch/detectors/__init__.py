"""Rule-based QueryWatch detectors."""

from .duplicate import detect_duplicate_queries
from .query_count import detect_query_count
from .slow import detect_slow_queries

__all__ = [
    "detect_duplicate_queries",
    "detect_query_count",
    "detect_slow_queries",
]
