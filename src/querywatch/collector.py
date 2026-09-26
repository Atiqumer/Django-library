"""Database query collection using Django's ``execute_wrapper`` API."""

from __future__ import annotations

from collections.abc import Callable, Iterator
from contextlib import contextmanager
from time import perf_counter
from typing import Any

from django.db.backends.base.base import BaseDatabaseWrapper

from .models import QueryRecord


class QueryCollector:
    """Collect query executions within one or more explicit capture scopes."""

    def __init__(self) -> None:
        self.records: list[QueryRecord] = []
        self._capture_depth: dict[int, int] = {}

    @contextmanager
    def capture(self, connection: BaseDatabaseWrapper) -> Iterator[None]:
        """Capture executions made through ``connection`` for this scope."""
        connection_id = id(connection)
        depth = self._capture_depth.get(connection_id, 0)
        self._capture_depth[connection_id] = depth + 1
        if depth:
            try:
                yield
            finally:
                self._leave_capture(connection_id)
            return

        try:
            with connection.execute_wrapper(self._wrapper_for(connection.alias)):
                yield
        finally:
            self._leave_capture(connection_id)

    def _leave_capture(self, connection_id: int) -> None:
        depth = self._capture_depth[connection_id] - 1
        if depth:
            self._capture_depth[connection_id] = depth
        else:
            del self._capture_depth[connection_id]

    def _wrapper_for(self, database: str) -> Callable[..., Any]:
        def wrapper(
            execute: Callable[..., Any],
            sql: str,
            params: object,
            many: bool,
            context: dict[str, Any],
        ) -> Any:
            started_at = perf_counter()
            success = False
            try:
                result = execute(sql, params, many, context)
                success = True
                return result
            finally:
                self.records.append(
                    QueryRecord(
                        sql=sql,
                        params=params,
                        duration_ms=(perf_counter() - started_at) * 1_000,
                        database=database,
                        many=many,
                        success=success,
                    )
                )

        return wrapper
