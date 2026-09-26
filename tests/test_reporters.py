import json

from querywatch.models import AnalysisReport, Finding, QuerySummary
from querywatch.reporters.console import format_console_report
from querywatch.reporters.json import format_json_report


def report() -> AnalysisReport:
    return AnalysisReport(
        summary=QuerySummary(
            query_count=3,
            total_duration_ms=12.3,
            slow_query_count=1,
            duplicate_group_count=1,
        ),
        aggregates=(),
        findings=(
            Finding(
                rule="slow-query",
                severity="warning",
                title="Slow query",
                message="Query exceeded the configured duration threshold.",
                evidence={"duration_ms": 100.0, "threshold_ms": 100.0},
                suggestion="Review the query shape and indexes.",
                fingerprint="a" * 64,
            ),
        ),
    )


def test_console_report_includes_summary_and_explainable_finding() -> None:
    output = format_console_report(report())

    assert "QueryWatch" in output
    assert "Queries: 3" in output
    assert "Total DB time: 12.3ms" in output
    assert "WARNING  Slow query" in output
    assert "duration_ms: 100.0" in output
    assert "Suggestion: Review the query shape and indexes." in output


def test_json_report_is_machine_readable_and_contains_no_parameters() -> None:
    payload = json.loads(format_json_report(report()))

    assert payload == {
        "summary": {
            "query_count": 3,
            "total_duration_ms": 12.3,
            "slow_queries": 1,
            "duplicate_groups": 1,
        },
        "findings": [
            {
                "rule": "slow-query",
                "severity": "warning",
                "title": "Slow query",
                "message": "Query exceeded the configured duration threshold.",
                "evidence": {"duration_ms": 100.0, "threshold_ms": 100.0},
                "suggestion": "Review the query shape and indexes.",
                "fingerprint": "a" * 64,
            }
        ],
    }
