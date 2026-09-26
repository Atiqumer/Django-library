"""Query grouping and aggregate statistics."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from .models import QueryAggregate, QueryRecord
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
