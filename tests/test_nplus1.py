from django.test import override_settings

from querywatch.detectors.nplus1 import detect_possible_n_plus_one
from querywatch.models import QueryRecord


def query_record(
    parameter: int | None,
    *,
    many: bool = False,
    success: bool = True,
) -> QueryRecord:
    return QueryRecord(
        sql="SELECT * FROM customers WHERE id = %s",
        params=None if parameter is None else [parameter],
        duration_ms=1.0,
        database="default",
        many=many,
        success=success,
    )


def test_nplus1_detector_reports_repeated_query_with_distinct_parameters() -> None:
    findings = detect_possible_n_plus_one(
        [query_record(1), query_record(2), query_record(3)]
    )

    assert len(findings) == 1
    finding = findings[0]
    assert finding.rule == "possible-n-plus-one"
    assert finding.severity == "warning"
    assert finding.title == "Possible N+1 query pattern"
    assert finding.evidence == {
        "execution_count": 3,
        "distinct_parameter_count": 3,
        "threshold": 3,
        "database": "default",
    }


def test_nplus1_detector_ignores_repeated_query_with_same_parameters() -> None:
    assert detect_possible_n_plus_one(
        [query_record(1), query_record(1), query_record(1)]
    ) == []


def test_nplus1_detector_ignores_batch_and_failed_queries() -> None:
    assert detect_possible_n_plus_one(
        [
            query_record(1, many=True),
            query_record(2, many=True),
            query_record(3, many=True),
            query_record(4, success=False),
            query_record(5, success=False),
            query_record(6, success=False),
        ]
    ) == []


@override_settings(QUERYWATCH_NPLUS1_THRESHOLD=4)
def test_nplus1_detector_uses_configured_threshold() -> None:
    findings = detect_possible_n_plus_one(
        [query_record(1), query_record(2), query_record(3), query_record(4)]
    )

    assert len(findings) == 1
    assert findings[0].evidence["threshold"] == 4
