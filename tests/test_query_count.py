from django.test import override_settings

from querywatch.detectors.query_count import detect_query_count
from querywatch.models import QueryRecord


def query_records(count: int) -> list[QueryRecord]:
    return [
        QueryRecord(
            sql="SELECT * FROM orders",
            params=None,
            duration_ms=1.0,
            database="default",
            many=False,
            success=True,
        )
        for _ in range(count)
    ]


def test_query_count_detector_is_disabled_by_default() -> None:
    assert detect_query_count(query_records(20)) == []


@override_settings(QUERYWATCH_MAX_QUERIES=10)
def test_query_count_detector_allows_count_at_limit() -> None:
    assert detect_query_count(query_records(10)) == []


@override_settings(QUERYWATCH_MAX_QUERIES=10)
def test_query_count_detector_reports_count_above_limit() -> None:
    findings = detect_query_count(query_records(16))

    assert len(findings) == 1
    finding = findings[0]
    assert finding.rule == "query-count"
    assert finding.severity == "error"
    assert finding.title == "Query count threshold exceeded"
    assert finding.evidence == {
        "actual_queries": 16,
        "max_queries": 10,
        "exceeded_by": 6,
    }
