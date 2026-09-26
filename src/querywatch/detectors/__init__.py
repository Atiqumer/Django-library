"""Rule-based QueryWatch detectors."""

from .duplicate import detect_duplicate_queries
from .slow import detect_slow_queries

__all__ = ["detect_duplicate_queries", "detect_slow_queries"]
