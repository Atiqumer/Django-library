"""Human- and machine-readable QueryWatch report formatters."""

from .console import format_console_report
from .json import format_json_report

__all__ = ["format_console_report", "format_json_report"]
