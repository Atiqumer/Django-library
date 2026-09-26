"""Slow-query detection."""

from __future__ import annotations

from collections.abc import Iterable

from ..config import slow_query_threshold_ms
from ..models import Finding, QueryRecord
from ..normalizer import fingerprint_sql


def detect_slow_queries(records: Iterable[QueryRecord]) -> list[Finding]:
    """Return findings for queries at or above the configured threshold."""
    threshold_ms = slow_query_threshold_ms()
    findings: list[Finding] = []

    for record in records:
        if record.duration_ms < threshold_ms:
            continue

        findings.append(
            Finding(
                rule="slow-query",
                severity="warning",
                title="Slow query",
                message="Query exceeded the configured duration threshold.",
                evidence={
                    "duration_ms": record.duration_ms,
                    "threshold_ms": threshold_ms,
                    "database": record.database,
                },
                suggestion="Review the query shape, indexes, and execution plan.",
                fingerprint=fingerprint_sql(record.sql),
            )
        )

    return findings
