import pytest
from django.db import connection

from querywatch import QueryCollector


@pytest.mark.django_db
def test_collector_captures_one_query() -> None:
    collector = QueryCollector()

    with collector.capture(connection):
        with connection.cursor() as cursor:
            cursor.execute("SELECT %s", [1])
            assert cursor.fetchone() == (1,)

    assert len(collector.records) == 1
    record = collector.records[0]
    assert record.sql == "SELECT %s"
    assert record.params == [1]
    assert record.database == "default"
    assert record.many is False
    assert record.success is True
    assert record.duration_ms >= 0
