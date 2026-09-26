import pytest
from django.db import DatabaseError, connection, connections

from querywatch import QueryCollector
from tests.testapp.models import Customer


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


@pytest.mark.django_db
def test_collector_captures_write_queries() -> None:
    collector = QueryCollector()

    with collector.capture(connection):
        customer = Customer.objects.create(name="Ada")
        Customer.objects.filter(pk=customer.pk).update(name="Grace")
        Customer.objects.filter(pk=customer.pk).delete()

    statements = "\n".join(record.sql.upper() for record in collector.records)
    assert "INSERT" in statements
    assert "UPDATE" in statements
    assert "DELETE" in statements
    assert all(record.success for record in collector.records)


@pytest.mark.django_db
def test_collector_captures_many_execution() -> None:
    with connection.cursor() as cursor:
        cursor.execute("CREATE TABLE querywatch_batch_test (value integer)")

    collector = QueryCollector()
    with collector.capture(connection):
        with connection.cursor() as cursor:
            cursor.executemany(
                "INSERT INTO querywatch_batch_test (value) VALUES (%s)",
                [(1,), (2,)],
            )

    with connection.cursor() as cursor:
        cursor.execute("DROP TABLE querywatch_batch_test")

    assert len(collector.records) == 1
    assert collector.records[0].many is True
    assert collector.records[0].success is True


@pytest.mark.django_db
def test_collector_records_and_reraises_database_error() -> None:
    collector = QueryCollector()

    with pytest.raises(DatabaseError):
        with collector.capture(connection):
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM querywatch_missing_table")

    assert len(collector.records) == 1
    assert collector.records[0].success is False


@pytest.mark.django_db
def test_collector_supports_zero_queries() -> None:
    collector = QueryCollector()

    with collector.capture(connection):
        pass

    assert collector.records == []


@pytest.mark.django_db(databases={"default", "analytics"})
def test_collector_records_database_aliases() -> None:
    collector = QueryCollector()

    with collector.capture(connections["default"]):
        with connections["default"].cursor() as cursor:
            cursor.execute("SELECT 1")
    with collector.capture(connections["analytics"]):
        with connections["analytics"].cursor() as cursor:
            cursor.execute("SELECT 1")

    assert {record.database for record in collector.records} == {"default", "analytics"}


@pytest.mark.django_db
def test_collector_does_not_duplicate_nested_capture_records() -> None:
    collector = QueryCollector()

    with collector.capture(connection):
        with collector.capture(connection):
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")

    assert len(collector.records) == 1
