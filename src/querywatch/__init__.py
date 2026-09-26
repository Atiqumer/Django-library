"""Django QueryWatch: database-performance analysis for Django."""

from .collector import QueryCollector
from .models import QueryRecord

__all__ = ["QueryCollector", "QueryRecord"]

