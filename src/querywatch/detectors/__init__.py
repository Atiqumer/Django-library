"""Rule-based QueryWatch detectors."""

from .duplicate import detect_duplicate_queries
from .nplus1 import detect_possible_n_plus_one
from .query_count import detect_query_count
from .slow import detect_slow_queries

__all__ = [
    "detect_duplicate_queries",
    "detect_possible_n_plus_one",
    "detect_query_count",
    "detect_slow_queries",
]
