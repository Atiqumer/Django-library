"""Request-level Django integration for QueryWatch."""

import logging
from collections.abc import Callable
from contextlib import ExitStack
from typing import Any

from django.db import connections

from .analyzer import analyze_queries
from .collector import QueryCollector
from .config import is_enabled, output_format
from .reporters.console import format_console_report
from .reporters.json import format_json_report


logger = logging.getLogger("querywatch")


class QueryWatchMiddleware:
    """Collect and report database activity for each synchronous request.

    Django adapts this synchronous middleware when needed. Native async
    request instrumentation is intentionally not claimed in v0.1.
    """

    sync_capable = True
    async_capable = False

    def __init__(self, get_response: Callable[[Any], Any]) -> None:
        self.get_response = get_response

    def __call__(self, request: Any) -> Any:
        if not is_enabled():
            return self.get_response(request)

        collector = QueryCollector()
        try:
            with ExitStack() as stack:
                for alias in connections:
                    stack.enter_context(collector.capture(connections[alias]))
                return self.get_response(request)
        finally:
            self._emit_report_safely(collector)

    def _emit_report_safely(self, collector: QueryCollector) -> None:
        """Render a report without changing the application's behavior."""
        try:
            report = analyze_queries(collector.records)
            match output_format():
                case "console":
                    logger.info(format_console_report(report))
                case "json":
                    logger.info(format_json_report(report))
                case "none":
                    return
        except Exception:
            logger.exception("QueryWatch could not produce a request report.")
