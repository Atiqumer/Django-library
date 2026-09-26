"""Conservative possible-N+1 query-pattern detection."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from hashlib import sha256

from ..config import nplus1_threshold
from ..models import Finding, QueryRecord
from ..normalizer import fingerprint_sql


@dataclass(slots=True)
class _NPlusOneCandidate:
    execution_count: int = 0
    parameter_fingerprints: set[bytes] = field(default_factory=set)


def detect_possible_n_plus_one(records: Iterable[QueryRecord]) -> list[Finding]:
    """Find repeated query patterns with distinct parameters.

    This intentionally reports only a possible N+1 pattern. It cannot infer
    the calling source code or a specific Django relationship from SQL alone.
    """
    threshold = nplus1_threshold()
    candidates: dict[tuple[str, str], _NPlusOneCandidate] = {}

    for record in records:
        if not record.success or record.many or record.params is None:
            continue

        fingerprint = fingerprint_sql(record.sql)
        key = (record.database, fingerprint)
        candidate = candidates.setdefault(key, _NPlusOneCandidate())
        candidate.execution_count += 1
        candidate.parameter_fingerprints.add(_parameter_fingerprint(record.params))

    return [
        Finding(
            rule="possible-n-plus-one",
            severity="warning",
            title="Possible N+1 query pattern",
            message=(
                "A query pattern was executed repeatedly with different "
                "parameters. This may indicate repeated relationship access "
                "inside a loop."
            ),
            evidence={
                "execution_count": candidate.execution_count,
                "distinct_parameter_count": len(candidate.parameter_fingerprints),
                "threshold": threshold,
                "database": database,
            },
            suggestion="Consider select_related() or prefetch_related() where appropriate.",
            fingerprint=fingerprint,
        )
        for (database, fingerprint), candidate in candidates.items()
        if candidate.execution_count >= threshold
        and len(candidate.parameter_fingerprints) >= threshold
    ]


def _parameter_fingerprint(params: object) -> bytes:
    """Create an in-memory comparison token without exposing parameter values."""
    return sha256(repr(params).encode("utf-8", errors="backslashreplace")).digest()
