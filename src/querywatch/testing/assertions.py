"""Query-budget assertions for Django tests."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import ExitStack, contextmanager

from django.db import connections

from ..analyzer import analyze_queries
from ..collector import QueryCollector
from ..models import AnalysisReport, Finding


class QueryWatchError(AssertionError):
    """Raised when a QueryWatch query budget is exceeded."""

    def __init__(self, *, max_queries: int, report: AnalysisReport) -> None:
        self.actual_queries = report.summary.query_count
        self.max_queries = max_queries
        self.exceeded_by = self.actual_queries - max_queries
        budget_finding = Finding(
            rule="query-budget",
            severity="error",
            title="Query budget exceeded",
            message="The test exceeded its configured query budget.",
            evidence={
                "actual_queries": self.actual_queries,
                "max_queries": max_queries,
                "exceeded_by": self.exceeded_by,
            },
            suggestion="Review duplicate queries and repeated database access.",
            fingerprint=None,
        )
        self.findings: tuple[Finding, ...] = report.findings + (budget_finding,)
        self.report = report
        super().__init__(
            "Query budget exceeded. "
            f"Expected: <= {max_queries}. "
            f"Actual: {self.actual_queries}. "
            f"Exceeded by: {self.exceeded_by}."
        )


@contextmanager
def assert_queries(*, max_queries: int) -> Iterator[None]:
    """Assert that a block performs no more than ``max_queries`` database calls.

    All configured Django database aliases are instrumented for the duration
    of the block. Application exceptions always propagate unchanged.
    """
    _validate_max_queries(max_queries)
    collector = QueryCollector()

    with ExitStack() as stack:
        for alias in connections:
            stack.enter_context(collector.capture(connections[alias]))
        yield

    report = analyze_queries(collector.records)
    if report.summary.query_count > max_queries:
        raise QueryWatchError(max_queries=max_queries, report=report)


def _validate_max_queries(value: int) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        message = "max_queries must be a non-negative integer."
        raise ValueError(message)
