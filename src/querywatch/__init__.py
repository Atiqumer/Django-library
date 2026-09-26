"""Django QueryWatch: database-performance analysis for Django."""

from .analyzer import aggregate_queries, analyze_queries
from .collector import QueryCollector
from .models import AnalysisReport, Finding, QueryAggregate, QueryRecord, QuerySummary
from .normalizer import fingerprint_sql, normalize_sql
from .testing import QueryWatchError, assert_queries

__all__ = [
    "AnalysisReport",
    "Finding",
    "QueryAggregate",
    "QueryCollector",
    "QueryRecord",
    "QuerySummary",
    "QueryWatchError",
    "aggregate_queries",
    "analyze_queries",
    "assert_queries",
    "fingerprint_sql",
    "normalize_sql",
]
