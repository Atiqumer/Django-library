"""Data structures used by QueryWatch."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class QueryRecord:
    """A single database execution observed by QueryWatch.

    ``duration_ms`` is measured with a monotonic clock and is expressed in
    milliseconds. SQL and parameters are retained only in the in-memory
    collector session.
    """

    sql: str
    params: object
    duration_ms: float
    database: str
    many: bool
    success: bool


@dataclass(frozen=True, slots=True)
class QueryAggregate:
    """Aggregate execution statistics for one normalized SQL fingerprint."""

    fingerprint: str
    normalized_sql: str
    execution_count: int
    total_duration_ms: float
    average_duration_ms: float
    minimum_duration_ms: float
    maximum_duration_ms: float
