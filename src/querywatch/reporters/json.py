"""JSON QueryWatch report formatting."""

from __future__ import annotations

import json
from typing import Any

from ..models import AnalysisReport, Finding


def format_json_report(report: AnalysisReport) -> str:
    """Serialize an analysis report into stable, machine-readable JSON."""
    return json.dumps(report_to_dict(report), sort_keys=True)


def report_to_dict(report: AnalysisReport) -> dict[str, Any]:
    """Convert an analysis report to JSON-compatible built-in structures."""
    summary = report.summary
    return {
        "summary": {
            "query_count": summary.query_count,
            "total_duration_ms": summary.total_duration_ms,
            "slow_queries": summary.slow_query_count,
            "duplicate_groups": summary.duplicate_group_count,
        },
        "findings": [_finding_to_dict(finding) for finding in report.findings],
    }


def _finding_to_dict(finding: Finding) -> dict[str, Any]:
    return {
        "rule": finding.rule,
        "severity": finding.severity,
        "title": finding.title,
        "message": finding.message,
        "evidence": dict(finding.evidence),
        "suggestion": finding.suggestion,
        "fingerprint": finding.fingerprint,
    }
