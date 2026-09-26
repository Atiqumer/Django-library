# Changelog

All notable changes to this project are documented here.

## [0.1.0] - Unreleased

### Added

- Django database instrumentation using `connection.execute_wrapper()`.
- In-memory query collection with timing, aliases, batch state, and failures.
- Conservative SQL normalization and deterministic SHA-256 fingerprints.
- Query aggregation with execution and duration statistics.
- Slow-query, duplicate-query, query-count, and possible-N+1 detectors.
- Plain-text and JSON report formatters.
- Request-level synchronous middleware with multi-database instrumentation.
- `assert_queries(max_queries=...)` query-budget testing API.
- SQLite-backed unit and Django integration tests.
