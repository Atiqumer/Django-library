"""Duplicate-query detection."""

from __future__ import annotations

from collections.abc import Iterable

from ..config import duplicate_query_threshold
from ..models import Finding, QueryAggregate


def detect_duplicate_queries(
    aggregates: Iterable[QueryAggregate],
) -> list[Finding]:
    """Return findings for query patterns repeated within one analysis scope."""
    threshold = duplicate_query_threshold()
    findings: list[Finding] = []

    for aggregate in aggregates:
        if aggregate.execution_count < threshold:
            continue

        findings.append(
            Finding(
                rule="duplicate-query",
                severity="info",
                title="Duplicate query",
                message="The same query pattern was executed repeatedly.",
                evidence={
                    "execution_count": aggregate.execution_count,
                    "total_duration_ms": aggregate.total_duration_ms,
                    "average_duration_ms": aggregate.average_duration_ms,
                    "threshold": threshold,
                },
                suggestion="Review whether repeated database access can be batched.",
                fingerprint=aggregate.fingerprint,
            )
        )

    return findings
