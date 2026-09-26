import pytest
from django.db import connection

from querywatch.testing import QueryWatchError, assert_queries


def execute_select() -> None:
    with connection.cursor() as cursor:
        cursor.execute("SELECT %s", [1])
        cursor.fetchone()


@pytest.mark.django_db
def test_assert_queries_allows_queries_within_budget() -> None:
    with assert_queries(max_queries=1):
        execute_select()


@pytest.mark.django_db
def test_assert_queries_raises_error_with_structured_details() -> None:
    with pytest.raises(QueryWatchError) as error:
        with assert_queries(max_queries=1):
            execute_select()
            execute_select()

    budget_error = error.value
    assert budget_error.actual_queries == 2
    assert budget_error.max_queries == 1
    assert budget_error.findings
    assert "Expected: <= 1" in str(budget_error)
    assert "Actual: 2" in str(budget_error)


@pytest.mark.django_db
def test_assert_queries_allows_zero_queries_with_zero_budget() -> None:
    with assert_queries(max_queries=0):
        pass
