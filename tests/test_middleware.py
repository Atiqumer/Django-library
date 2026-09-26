import json
from unittest.mock import patch

import pytest
from django.db import connection, connections
from django.http import HttpResponse
from django.test import RequestFactory, override_settings

from querywatch.middleware import QueryWatchMiddleware


def response_with_query(request: object) -> HttpResponse:
    with connection.cursor() as cursor:
        cursor.execute("SELECT %s", [1])
        cursor.fetchone()
    return HttpResponse("ok")


def response_with_multiple_database_queries(request: object) -> HttpResponse:
    for alias in ("default", "analytics"):
        with connections[alias].cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
    return HttpResponse("ok")


@pytest.mark.django_db
@override_settings(QUERYWATCH_ENABLED=True, QUERYWATCH_OUTPUT="console")
def test_middleware_collects_and_emits_request_report() -> None:
    middleware = QueryWatchMiddleware(response_with_query)

    with patch("querywatch.middleware.logger") as logger:
        response = middleware(RequestFactory().get("/orders/"))

    assert response.status_code == 200
    logger.info.assert_called_once()
    assert "Queries: 1" in logger.info.call_args.args[0]


@pytest.mark.django_db
@override_settings(QUERYWATCH_ENABLED=False)
def test_middleware_does_not_emit_when_disabled() -> None:
    middleware = QueryWatchMiddleware(response_with_query)

    with patch("querywatch.middleware.logger") as logger:
        response = middleware(RequestFactory().get("/orders/"))

    assert response.status_code == 200
    logger.info.assert_not_called()


@pytest.mark.django_db
@override_settings(QUERYWATCH_ENABLED=True, QUERYWATCH_OUTPUT="json")
def test_middleware_emits_machine_readable_json() -> None:
    middleware = QueryWatchMiddleware(response_with_query)

    with patch("querywatch.middleware.logger") as logger:
        response = middleware(RequestFactory().get("/orders/"))

    assert response.status_code == 200
    payload = json.loads(logger.info.call_args.args[0])
    assert payload["summary"]["query_count"] == 1
    assert "params" not in logger.info.call_args.args[0]


@pytest.mark.django_db(databases={"default", "analytics"})
@override_settings(QUERYWATCH_ENABLED=True, QUERYWATCH_OUTPUT="json")
def test_middleware_captures_all_configured_database_aliases() -> None:
    middleware = QueryWatchMiddleware(response_with_multiple_database_queries)

    with patch("querywatch.middleware.logger") as logger:
        response = middleware(RequestFactory().get("/orders/"))

    assert response.status_code == 200
    payload = json.loads(logger.info.call_args.args[0])
    assert payload["summary"]["query_count"] == 2


@override_settings(QUERYWATCH_ENABLED=True, QUERYWATCH_OUTPUT="none")
def test_middleware_preserves_downstream_exception() -> None:
    def raising_response(request: object) -> HttpResponse:
        raise RuntimeError("application failure")

    middleware = QueryWatchMiddleware(raising_response)

    with pytest.raises(RuntimeError, match="application failure"):
        middleware(RequestFactory().get("/orders/"))
