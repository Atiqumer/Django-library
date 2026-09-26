from django.test import override_settings

from querywatch.detectors.slow import detect_slow_queries
from querywatch.models import QueryRecord


def query_record(duration_ms: float) -> QueryRecord:
    return QueryRecord(
        sql="SELECT * FROM orders WHERE id = %s",
        params=[1],
        duration_ms=duration_ms,
        database="default",
        many=False,
        success=True,
    )


def test_slow_detector_ignores_query_below_default_threshold() -> None:
    assert detect_slow_queries([query_record(50.0)]) == []


def test_slow_detector_flags_query_at_default_threshold() -> None:
    findings = detect_slow_queries([query_record(100.0)])

    assert len(findings) == 1
    finding = findings[0]
    assert finding.rule == "slow-query"
    assert finding.severity == "warning"
    assert finding.title == "Slow query"
    assert finding.evidence == {
        "duration_ms": 100.0,
        "threshold_ms": 100.0,
        "database": "default",
    }
    assert finding.fingerprint is not None


def test_slow_detector_flags_query_above_default_threshold() -> None:
    findings = detect_slow_queries([query_record(150.0)])

    assert len(findings) == 1
    assert findings[0].evidence["duration_ms"] == 150.0


@override_settings(QUERYWATCH_SLOW_QUERY_MS=200)
def test_slow_detector_uses_configured_threshold() -> None:
    records = [query_record(150.0), query_record(200.0)]

    findings = detect_slow_queries(records)

    assert len(findings) == 1
    assert findings[0].evidence["duration_ms"] == 200.0
    assert findings[0].evidence["threshold_ms"] == 200.0
