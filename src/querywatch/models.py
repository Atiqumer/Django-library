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

