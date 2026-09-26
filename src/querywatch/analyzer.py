"""Query grouping and aggregate statistics."""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass

from .detectors.duplicate import detect_duplicate_queries
from .detectors.nplus1 import detect_possible_n_plus_one
from .detectors.query_count import detect_query_count
from .detectors.slow import detect_slow_queries
from .models import AnalysisReport, QueryAggregate, QueryRecord, QuerySummary
from .normalizer import fingerprint_normalized_sql, normalize_sql


@dataclass(slots=True)
class _AggregateAccumulator:
    normalized_sql: str
    execution_count: int
    total_duration_ms: float
    minimum_duration_ms: float
    maximum_duration_ms: float

    def add(self, duration_ms: float) -> None:
        self.execution_count += 1
        self.total_duration_ms += duration_ms
        self.minimum_duration_ms = min(self.minimum_duration_ms, duration_ms)
        self.maximum_duration_ms = max(self.maximum_duration_ms, duration_ms)


def aggregate_queries(records: Iterable[QueryRecord]) -> dict[str, QueryAggregate]:
    """Group records by fingerprint and calculate execution-time statistics.

    The iterable is consumed once. The returned dictionary preserves the
    first-seen fingerprint order, which keeps reports deterministic.
    """
    accumulators: dict[str, _AggregateAccumulator] = {}

    for record in records:
        normalized_sql = normalize_sql(record.sql)
        fingerprint = fingerprint_normalized_sql(normalized_sql)
        accumulator = accumulators.get(fingerprint)
        if accumulator is None:
            accumulators[fingerprint] = _AggregateAccumulator(
                normalized_sql=normalized_sql,
                execution_count=1,
                total_duration_ms=record.duration_ms,
                minimum_duration_ms=record.duration_ms,
                maximum_duration_ms=record.duration_ms,
            )
        else:
            accumulator.add(record.duration_ms)

    return {
        fingerprint: QueryAggregate(
            fingerprint=fingerprint,
            normalized_sql=accumulator.normalized_sql,
            execution_count=accumulator.execution_count,
            total_duration_ms=accumulator.total_duration_ms,
            average_duration_ms=(
                accumulator.total_duration_ms / accumulator.execution_count
            ),
            minimum_duration_ms=accumulator.minimum_duration_ms,
            maximum_duration_ms=accumulator.maximum_duration_ms,
        )
        for fingerprint, accumulator in accumulators.items()
    }


def analyze_queries(records: Sequence[QueryRecord]) -> AnalysisReport:
    """Analyze one query-collection scope and return its complete report."""
    aggregates = aggregate_queries(records)
    slow_findings = detect_slow_queries(records)
    duplicate_findings = detect_duplicate_queries(aggregates.values())
    count_findings = detect_query_count(records)
    nplus1_findings = detect_possible_n_plus_one(records)

    findings = tuple(
        slow_findings + duplicate_findings + count_findings + nplus1_findings
    )
    return AnalysisReport(
        summary=QuerySummary(
            query_count=len(records),
            total_duration_ms=sum(record.duration_ms for record in records),
            slow_query_count=len(slow_findings),
            duplicate_group_count=len(duplicate_findings),
        ),
        aggregates=tuple(aggregates.values()),
        findings=findings,
    )
