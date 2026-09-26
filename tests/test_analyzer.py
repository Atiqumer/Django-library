from querywatch.analyzer import aggregate_queries
from querywatch.models import QueryRecord


def query_record(sql: str, duration_ms: float) -> QueryRecord:
    return QueryRecord(
        sql=sql,
        params=[1],
        duration_ms=duration_ms,
        database="default",
        many=False,
        success=True,
    )


def test_aggregate_queries_calculates_statistics_per_fingerprint() -> None:
    records = [
        query_record("SELECT * FROM orders WHERE id = %s", 1.5),
        query_record(" SELECT *\nFROM orders WHERE id = %s ", 4.0),
        query_record("DELETE FROM orders WHERE id = %s", 2.0),
    ]

    aggregates = aggregate_queries(records)

    assert len(aggregates) == 2
    select_group = next(
        group
        for group in aggregates.values()
        if group.normalized_sql == "SELECT * FROM orders WHERE id = %s"
    )
    assert select_group.execution_count == 2
    assert select_group.total_duration_ms == 5.5
    assert select_group.average_duration_ms == 2.75
    assert select_group.minimum_duration_ms == 1.5
    assert select_group.maximum_duration_ms == 4.0


def test_aggregate_queries_returns_no_groups_for_no_records() -> None:
    assert aggregate_queries([]) == {}
