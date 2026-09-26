from django.test import override_settings

from querywatch.analyzer import analyze_queries
from querywatch.models import QueryRecord


def query_record(parameter: int, duration_ms: float = 100.0) -> QueryRecord:
    return QueryRecord(
        sql="SELECT * FROM customers WHERE id = %s",
        params=[parameter],
        duration_ms=duration_ms,
        database="default",
        many=False,
        success=True,
    )


@override_settings(QUERYWATCH_MAX_QUERIES=2)
def test_analyze_queries_builds_summary_aggregates_and_findings() -> None:
    report = analyze_queries([query_record(1), query_record(2), query_record(3)])

    assert report.summary.query_count == 3
    assert report.summary.total_duration_ms == 300.0
    assert report.summary.slow_query_count == 3
    assert report.summary.duplicate_group_count == 1
    assert len(report.aggregates) == 1
    assert [finding.rule for finding in report.findings] == [
        "slow-query",
        "slow-query",
        "slow-query",
        "duplicate-query",
        "query-count",
        "possible-n-plus-one",
    ]


def test_analyze_queries_handles_zero_records() -> None:
    report = analyze_queries([])

    assert report.summary.query_count == 0
    assert report.summary.total_duration_ms == 0
    assert report.summary.slow_query_count == 0
    assert report.summary.duplicate_group_count == 0
    assert report.aggregates == ()
    assert report.findings == ()
