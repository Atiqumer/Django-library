from django.test import override_settings

from querywatch.detectors.duplicate import detect_duplicate_queries
from querywatch.models import QueryAggregate


def query_aggregate(execution_count: int) -> QueryAggregate:
    return QueryAggregate(
        fingerprint="a" * 64,
        normalized_sql="SELECT * FROM orders WHERE id = %s",
        execution_count=execution_count,
        total_duration_ms=12.0,
        average_duration_ms=4.0,
        minimum_duration_ms=2.0,
        maximum_duration_ms=6.0,
    )


def test_duplicate_detector_ignores_group_below_default_threshold() -> None:
    assert detect_duplicate_queries([query_aggregate(2)]) == []


def test_duplicate_detector_reports_group_at_default_threshold() -> None:
    findings = detect_duplicate_queries([query_aggregate(3)])

    assert len(findings) == 1
    finding = findings[0]
    assert finding.rule == "duplicate-query"
    assert finding.severity == "info"
    assert finding.title == "Duplicate query"
    assert finding.evidence == {
        "execution_count": 3,
        "total_duration_ms": 12.0,
        "average_duration_ms": 4.0,
        "threshold": 3,
    }
    assert finding.fingerprint == "a" * 64


@override_settings(QUERYWATCH_DUPLICATE_THRESHOLD=5)
def test_duplicate_detector_uses_configured_threshold() -> None:
    findings = detect_duplicate_queries([query_aggregate(4), query_aggregate(5)])

    assert len(findings) == 1
    assert findings[0].evidence["execution_count"] == 5
    assert findings[0].evidence["threshold"] == 5
