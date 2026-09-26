# Django QueryWatch

Automated database-performance analysis for Django.

Source code and issue tracking: [Atiqumer/django-querywatch](https://github.com/Atiqumer/django-querywatch).

QueryWatch observes database executions made by a Django request or test,
groups query patterns, and turns suspicious behavior into explainable
findings. It is a local-development and test/CI tool; it does not modify
queries, create database tables, or send data to an external service.

> **Status:** pre-alpha. The public API may change before 1.0.

## Why QueryWatch?

Query viewers show what ran. QueryWatch focuses on what may deserve attention:

- queries at or above a configurable duration threshold;
- repeated query patterns;
- possible N+1 patterns with distinct parameters; and
- query budgets for tests.

Findings are rule-based and intentionally conservative. In particular, an
N+1 finding is described as *possible* because SQL alone cannot prove which
Python source line or Django relationship caused it.

## Compatibility

QueryWatch targets Python 3.12–3.14 and Django 5.2–6.1. SQLite is used for
the current test suite. PostgreSQL and MySQL compatibility verification is
planned before a stable release.

## Installation

After the package is published to PyPI:

```bash
python -m pip install django-query-sentinel
```

For development from a checkout, see [Development](#development).

## Quick start

```python
# settings.py

INSTALLED_APPS = [
    # ...
    "querywatch",
]

MIDDLEWARE = [
    # ...
    "querywatch.middleware.QueryWatchMiddleware",
]
```

The middleware logs a console report through the `querywatch` logger after
each synchronous request. Set `QUERYWATCH_OUTPUT = "none"` when you only want
to use the testing API.

## Configuration

```python
# settings.py

QUERYWATCH_ENABLED = True
QUERYWATCH_OUTPUT = "console"  # "console", "json", or "none"

QUERYWATCH_SLOW_QUERY_MS = 100
QUERYWATCH_DUPLICATE_THRESHOLD = 3
QUERYWATCH_NPLUS1_THRESHOLD = 3
QUERYWATCH_MAX_QUERIES = None  # Request-level finding; disabled
```

`QUERYWATCH_MAX_QUERIES` causes an error-level finding in request reports. It
does not change an HTTP response. To fail a test, use `assert_queries()`.

## Reports

Console output is intentionally dependency-free:

```text
QueryWatch
────────────────────────────────
Queries: 27
Total DB time: 84.3ms
Slow queries: 2
Duplicate groups: 4

Findings
────────────────────────────────
WARNING  Possible N+1 query pattern
A query pattern was executed repeatedly with different parameters.
```

Set `QUERYWATCH_OUTPUT = "json"` to log a machine-readable JSON object with a
summary and findings. Reports include structural evidence, timing values, and
fingerprints; they do not include query parameters.

## Query budgets

```python
from querywatch.testing import assert_queries


def test_dashboard(client):
    with assert_queries(max_queries=10):
        response = client.get("/dashboard/")

    assert response.status_code == 200
```

If the budget is exceeded, `QueryWatchError` exposes `actual_queries`,
`max_queries`, `exceeded_by`, `findings`, and `report` for programmatic
assertions.

## Detectors

| Detector | Default | Severity |
| --- | --- | --- |
| Slow query | `QUERYWATCH_SLOW_QUERY_MS = 100` | warning |
| Duplicate query | `QUERYWATCH_DUPLICATE_THRESHOLD = 3` | info |
| Possible N+1 | `QUERYWATCH_NPLUS1_THRESHOLD = 3` | warning |
| Query count | disabled (`QUERYWATCH_MAX_QUERIES = None`) | error |

## Privacy and safety

- Captured query data exists only in memory for the active scope.
- QueryWatch does not create models, migrations, caches, queues, or services.
- QueryWatch does not re-execute captured SQL and never runs `EXPLAIN ANALYZE`.
- Query parameters are not included in console or JSON reports.
- QueryWatch does not change a QuerySet, transaction, SQL statement, or result.

## Limitations

- Middleware instrumentation is synchronous. Native async instrumentation is
  not claimed in v0.1.
- SQL normalization is deliberately conservative; comments and PostgreSQL
  dollar-quoted strings are left unchanged.
- Possible-N+1 detection is heuristic and does not infer exact relationship
  names or source locations.
- This is not a production-monitoring service or a historical metrics store.

## Development

Requires Python 3.12+.

```bash
python -m pip install -e ".[dev]"
python -m ruff check .
python -m pytest
```

Run the complete test suite before submitting a change. Tests use an isolated
SQLite Django test database and require no network access.

## Packaging verification

Build both distribution formats locally:

```bash
python -m build
```

This creates a wheel and source distribution in `dist/`. Verify the wheel in
a fresh virtual environment before publishing:

```powershell
python -m venv .wheel-test
.\.wheel-test\Scripts\python -m pip install .\dist\django_query_sentinel-0.1.0-py3-none-any.whl
.\.wheel-test\Scripts\python -c "import querywatch; print(querywatch.__name__)"
```

Replace the wheel filename if the package version changes. Do not publish
until the wheel installs and imports successfully.

For the tag-based Trusted Publishing release process, see [RELEASING.md](RELEASING.md).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Please keep changes small, add tests
for behavior changes, and avoid new runtime dependencies unless there is a
concrete need.

## License

QueryWatch is released under the [MIT License](LICENSE).
