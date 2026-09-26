import pytest

from querywatch.normalizer import fingerprint_sql, normalize_sql


@pytest.mark.parametrize(
    ("first", "second", "expected"),
    [
        (
            "SELECT * FROM orders WHERE customer_id = %s",
            " SELECT  *\nFROM orders\tWHERE customer_id = %s ",
            "SELECT * FROM orders WHERE customer_id = %s",
        ),
        (
            "SELECT * FROM orders WHERE customer_id = %s",
            "SELECT * FROM orders WHERE customer_id = %s",
            "SELECT * FROM orders WHERE customer_id = %s",
        ),
    ],
)
def test_normalize_sql_groups_parameterized_query_shapes(
    first: str, second: str, expected: str
) -> None:
    assert normalize_sql(first) == expected
    assert normalize_sql(second) == expected
    assert fingerprint_sql(first) == fingerprint_sql(second)


def test_normalize_sql_preserves_whitespace_inside_string_literals() -> None:
    sql = "SELECT 'one   two' FROM orders"

    assert normalize_sql(sql) == sql


def test_normalize_sql_preserves_whitespace_inside_quoted_identifiers() -> None:
    sql = 'SELECT "column   name" FROM orders'

    assert normalize_sql(sql) == sql


def test_normalize_sql_does_not_normalize_sql_containing_comments() -> None:
    sql = "SELECT 1 -- a comment\nFROM orders"

    assert normalize_sql(sql) == sql


@pytest.mark.parametrize(
    "first, second",
    [
        ("SELECT * FROM orders WHERE id = 1", "SELECT * FROM orders WHERE id = 2"),
        ("SELECT * FROM orders WHERE total = 1.50", "SELECT * FROM orders WHERE total = 2.50"),
        (
            "SELECT * FROM orders WHERE public_id = 'a0b1c2d3'",
            "SELECT * FROM orders WHERE public_id = 'e4f5a6b7'",
        ),
        ("SELECT * FROM orders", "DELETE FROM orders"),
    ],
)
def test_normalize_sql_keeps_unparameterized_statements_distinct(
    first: str, second: str
) -> None:
    assert fingerprint_sql(first) != fingerprint_sql(second)
