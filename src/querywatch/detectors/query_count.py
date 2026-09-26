"""Query-count threshold detection."""

from __future__ import annotations

from collections.abc import Sequence

from ..config import max_queries
from ..models import Finding, QueryRecord


def detect_query_count(records: Sequence[QueryRecord]) -> list[Finding]:
    """Return a finding when the configured query-count limit is exceeded."""
    limit = max_queries()
    actual_queries = len(records)
    if limit is None or actual_queries <= limit:
        return []

    return [
        Finding(
            rule="query-count",
            severity="error",
            title="Query count threshold exceeded",
            message="The number of database queries exceeded the configured limit.",
            evidence={
                "actual_queries": actual_queries,
                "max_queries": limit,
                "exceeded_by": actual_queries - limit,
            },
            suggestion="Review duplicate queries and repeated database access.",
            fingerprint=None,
        )
    ]
