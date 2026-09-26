# Django QueryWatch --- Codex Build Specification

## 0. Purpose of This File

This document is the source-of-truth specification for building **Django
QueryWatch**, an open-source Python/Django package for
database-performance analysis.

Use this file as the primary project instruction when working with
Codex.

The goal is to build a real, maintainable, test-covered package that can
eventually be published to PyPI.

Do not treat this as a one-shot code-generation task. Build
incrementally, run tests after each meaningful change, and keep the
implementation aligned with this specification.

------------------------------------------------------------------------

# 1. Project Identity

## Package name

`django-querywatch`

## Python import name

`querywatch`

## Working title

**QueryWatch**

## Tagline

> Automated database-performance analysis for Django.

## One-sentence product definition

QueryWatch captures Django database activity, analyzes query patterns,
identifies suspicious behavior such as slow, duplicate, excessive, and
possible N+1 queries, explains the findings, and eventually allows
developers to enforce query budgets in tests and CI.

------------------------------------------------------------------------

# 2. Product Positioning

QueryWatch is NOT intended to be another generic SQL viewer.

Existing Django tooling already provides query inspection and profiling.
QueryWatch should instead focus on:

1.  Detecting suspicious query behavior.
2.  Turning raw query activity into actionable findings.
3.  Providing Django-aware suggestions.
4.  Allowing query budgets to be enforced in tests.
5.  Eventually detecting database-performance regressions in CI.

Core distinction:

> Debugging tools show developers what queries happened. QueryWatch
> should help explain what appears wrong with those queries.

Do not claim that QueryWatch is the first or only package to perform any
individual detection. The ecosystem already contains query profilers,
N+1 detectors, query counters, and Django debugging tools.

The project differentiator is the combination of:

-   lightweight instrumentation
-   query normalization/fingerprinting
-   actionable findings
-   Django-aware suggestions
-   query-budget testing
-   future regression detection

------------------------------------------------------------------------

# 3. Research Context

The implementation should use Django's official database instrumentation
mechanism:

``` python
connection.execute_wrapper()
```

Django documents this API for database instrumentation, including timing
and logging database executions.

Official documentation:

-   https://docs.djangoproject.com/en/6.1/topics/db/instrumentation/
-   https://docs.djangoproject.com/en/6.1/topics/db/optimization/
-   https://docs.djangoproject.com/en/6.1/ref/models/querysets/

Relevant ecosystem tools to be aware of:

-   Django Debug Toolbar
-   Django Silk
-   django-querycount
-   django-query-profiler
-   django-nplus1
-   nplusone
-   django-query-counter

QueryWatch must not simply copy their feature sets or implementation.

------------------------------------------------------------------------

# 4. Compatibility Target

## Supported Python

Target:

-   Python 3.12
-   Python 3.13
-   Python 3.14

## Supported Django

Target:

-   Django 5.2
-   Django 6.0
-   Django 6.1

Django 6.0 and 6.1 support Python 3.12, 3.13, and 3.14.

Django 5.2 supports Python 3.10--3.14, but QueryWatch intentionally
targets Python 3.12+ to keep the package modern and the compatibility
matrix manageable.

Do not add compatibility hacks for unsupported Django/Python versions
unless explicitly requested.

------------------------------------------------------------------------

# 5. Database Strategy

Initial development:

-   SQLite

Required compatibility testing before release:

-   SQLite
-   PostgreSQL
-   MySQL where practical

The package must not require a separate database for QueryWatch itself.

QueryWatch must NOT create its own Django models or migrations in v0.1.

No QueryWatch database tables.

No Redis.

No Celery.

No external cloud service.

No API key.

No AI API.

------------------------------------------------------------------------

# 6. Core Design Principles

Follow these principles throughout the implementation.

## 6.1 Lightweight

QueryWatch is a developer tool. Avoid unnecessary overhead.

## 6.2 No query re-execution

QueryWatch must not automatically execute a captured query again merely
to analyze it.

In particular, do not automatically run `EXPLAIN ANALYZE`.

Some database systems execute a query when `EXPLAIN ANALYZE` is used.

If deep database analysis is added later, it must be explicit and
opt-in.

## 6.3 Deterministic analysis

v0.1 analysis must be rule-based.

Do not introduce AI/LLM dependencies.

## 6.4 Explainable findings

Every finding should explain:

-   what was detected
-   why it was detected
-   evidence
-   possible impact
-   possible improvement

## 6.5 No false certainty

Especially for N+1 detection, use wording such as:

> Possible N+1 query pattern

rather than:

> This is definitely an N+1 query.

## 6.6 No automatic source-code modification

QueryWatch reports findings. It does not rewrite user code.

## 6.7 No production monitoring in v0.1

The initial release is a local-development and test/CI developer tool.

------------------------------------------------------------------------

# 7. v0.1 Scope

The first usable release must contain:

### Collector

-   SQL capture
-   parameters capture where safely available
-   execution duration
-   database alias
-   `many`
-   success/failure state

### Query analysis

-   query normalization
-   query fingerprinting
-   query grouping
-   aggregate statistics

### Detectors

-   query-count threshold
-   slow-query detection
-   duplicate-query detection
-   basic possible-N+1 detection
-   query-budget enforcement

### Reporting

-   terminal report
-   JSON report

### Testing API

At minimum:

``` python
with assert_queries(max_queries=10):
    ...
```

Do not attempt to build a web dashboard in v0.1.

------------------------------------------------------------------------

# 8. Explicitly Out of Scope for v0.1

Do NOT implement:

-   web dashboard
-   Chrome extension
-   cloud service
-   SaaS backend
-   Redis integration
-   Celery integration
-   AI/LLM analysis
-   automatic code fixes
-   automatic EXPLAIN ANALYZE
-   production monitoring
-   historical metrics database
-   distributed tracing
-   frontend application
-   authentication
-   user accounts
-   billing
-   hosted service

These can be considered later only after the core analyzer is stable.

------------------------------------------------------------------------

# 9. Target User Experience

A developer should eventually be able to install:

``` bash
pip install django-querywatch
```

Add QueryWatch to a Django project and receive a report similar to:

``` text
QueryWatch
────────────────────────────────────

Request: GET /orders/

Queries:        27
Total DB time:  84.3ms
Slow queries:    2
Duplicate groups: 4

Findings
────────────────────────────────────

WARNING  Possible N+1

19 similar queries were executed with
different parameters.

Possible improvement:
select_related("customer")


WARNING  Slow query

Duration: 183ms
Threshold: 100ms


INFO  Duplicate query

The same query pattern was executed 7 times.
```

The exact formatting can evolve.

Do not optimize for visual polish before correctness.

------------------------------------------------------------------------

# 10. Architecture

Target architecture:

``` text
                    Django Application
                           |
                           v
                  QueryWatch Middleware
                           |
                           v
                  Database Instrumentation
                           |
                           v
                     Query Collector
                           |
                           v
                      QueryRecord
                           |
                           v
                    SQL Normalizer
                           |
                           v
                    Query Fingerprint
                           |
                           v
                     Finding Engine
                           |
            +--------------+--------------+
            |              |              |
            v              v              v
       Slow Detector   Duplicate       N+1 Detector
                        Detector
            |              |              |
            +--------------+--------------+
                           |
                           v
                       Findings
                           |
                  +--------+--------+
                  |                 |
                  v                 v
               Console             JSON
                  |
                  v
             Test/CI API
```

------------------------------------------------------------------------

# 11. Repository Structure

Start with this structure:

``` text
django-querywatch/
│
├── pyproject.toml
├── README.md
├── LICENSE
├── CHANGELOG.md
├── CONTRIBUTING.md
├── .gitignore
│
├── src/
│   └── querywatch/
│       ├── __init__.py
│       ├── apps.py
│       ├── config.py
│       ├── middleware.py
│       │
│       ├── collector.py
│       ├── models.py
│       ├── normalizer.py
│       ├── analyzer.py
│       │
│       ├── detectors/
│       │   ├── __init__.py
│       │   ├── slow.py
│       │   ├── duplicate.py
│       │   ├── nplus1.py
│       │   └── budget.py
│       │
│       ├── reporters/
│       │   ├── __init__.py
│       │   ├── console.py
│       │   └── json.py
│       │
│       └── testing/
│           ├── __init__.py
│           └── assertions.py
│
└── tests/
    ├── __init__.py
    ├── conftest.py
    ├── test_collector.py
    ├── test_normalizer.py
    ├── test_slow.py
    ├── test_duplicate.py
    ├── test_nplus1.py
    └── test_budget.py
```

The structure may be refactored if implementation experience shows a
better design, but keep responsibilities separated.

------------------------------------------------------------------------

# 12. `QueryRecord`

Create a small internal representation for a captured query.

Conceptual fields:

``` python
QueryRecord(
    sql: str,
    params: object,
    duration: float,
    database: str,
    many: bool,
    success: bool,
)
```

Potential future fields:

``` text
timestamp
source_location
request_id
connection_alias
normalized_sql
fingerprint
```

Do not add fields just because they might be useful later.

Prefer small immutable/data-oriented structures where appropriate.

------------------------------------------------------------------------

# 13. Query Collection

Use Django's database instrumentation API.

Conceptually:

``` python
with connection.execute_wrapper(wrapper):
    ...
```

The wrapper receives the execution information from Django.

The implementation must correctly handle:

-   normal queries
-   queries using `many=True`
-   exceptions
-   nested execution where relevant
-   multiple database aliases
-   requests with zero queries

The collector must not alter the query or its parameters.

The collector must re-raise database exceptions after recording the
failure.

Do not swallow database errors.

------------------------------------------------------------------------

# 14. Timing

Measure duration around the actual execution:

``` text
start
  |
  v
execute query
  |
  v
end
```

Use a monotonic timer such as:

``` python
time.perf_counter()
```

Do not use wall-clock time for elapsed-duration measurement.

Store duration internally in seconds or milliseconds consistently.

Pick one internal representation and document it.

Recommended:

``` python
duration_ms: float
```

------------------------------------------------------------------------

# 15. Query Normalization

This is a foundational component.

Example raw SQL:

``` sql
SELECT * FROM users WHERE id = 1;
SELECT * FROM users WHERE id = 2;
SELECT * FROM users WHERE id = 3;
```

should be recognized as the same query pattern.

Target normalized representation:

``` text
SELECT * FROM users WHERE id = ?
```

However, do NOT write an unsafe or over-aggressive SQL parser.

The initial normalizer should be conservative.

Requirements:

1.  Never modify the original SQL.
2.  Preserve the raw SQL in `QueryRecord`.
3.  Generate a separate normalized representation.
4.  Avoid changing SQL semantics.
5.  Prefer false negatives over dangerous false positives.
6.  Add tests for every normalization rule.

Important:

Do not assume that replacing every number with `?` is safe.

SQL can contain:

-   numeric constants
-   decimal values
-   strings
-   identifiers containing numbers
-   PostgreSQL-specific syntax
-   JSON
-   timestamps
-   vendor-specific syntax

Start with conservative normalization based on Django's parameterized
SQL behavior where possible.

If a robust SQL parser is required, research available maintained
packages before adding a dependency.

------------------------------------------------------------------------

# 16. Query Fingerprints

After normalization:

``` text
normalized SQL
      |
      v
stable hash
      |
      v
fingerprint
```

Example:

``` text
fingerprint = sha256(normalized_sql).hexdigest()
```

The exact hash algorithm can change.

The fingerprint must be deterministic.

Do not use Python's built-in `hash()` for persistent/comparable
fingerprints because it is not stable across interpreter processes.

------------------------------------------------------------------------

# 17. Query Aggregation

For each fingerprint calculate:

``` text
execution_count
total_duration_ms
average_duration_ms
minimum_duration_ms
maximum_duration_ms
```

Example:

``` text
Fingerprint: abc123

Executions: 18
Total: 42.1ms
Average: 2.34ms
Min: 0.9ms
Max: 8.4ms
```

Aggregation must be request/session aware.

A query repeated in two different requests must not accidentally become
one request-level duplicate finding.

------------------------------------------------------------------------

# 18. Slow Query Detector

Configuration:

``` python
QUERYWATCH_SLOW_QUERY_MS = 100
```

Default:

``` text
100ms
```

If:

``` text
duration_ms >= threshold
```

create a finding.

Example:

``` text
WARNING Slow query

Duration: 327.4ms
Threshold: 100ms
```

The threshold should be configurable.

Do not hard-code it into detector logic.

------------------------------------------------------------------------

# 19. Duplicate Query Detector

A duplicate query means the same normalized query pattern appears
repeatedly within the analysis scope.

Configuration:

``` python
QUERYWATCH_DUPLICATE_THRESHOLD = 2
```

Potential default:

``` text
2 or 3
```

Choose a sensible default after tests.

Example:

``` text
SELECT ... WHERE id = ?
```

executed 14 times.

Finding:

``` text
INFO Duplicate query

Query pattern executed 14 times.

Total time: 31.2ms
Average: 2.2ms
```

Do not automatically classify every duplicate as N+1.

------------------------------------------------------------------------

# 20. Possible N+1 Detector

This detector must be conservative.

A basic candidate requires:

1.  Same normalized query/fingerprint.
2.  Repeated execution.
3.  Different parameter values where parameters are available.
4.  Repetition within a request/analysis scope.
5.  Enough repetitions to make the pattern suspicious.

Example:

``` text
SELECT ... FROM customer WHERE id = ?
SELECT ... FROM customer WHERE id = ?
SELECT ... FROM customer WHERE id = ?
```

with different IDs.

Potential finding:

``` text
WARNING Possible N+1 query pattern

The same query pattern was executed 18 times
with different parameters.

Possible cause:
database access inside a loop.

Possible improvement:
select_related("customer")
or
prefetch_related(...)
```

Important:

The detector must not claim it knows the exact Django relationship
unless there is reliable evidence.

Do not produce:

``` text
Definitely use select_related("customer")
```

from SQL alone.

Use:

``` text
Possible improvement:
consider select_related() / prefetch_related()
```

unless source/ORM metadata provides stronger evidence.

------------------------------------------------------------------------

# 21. Query Budget

QueryWatch should support a testing API.

Target:

``` python
from querywatch.testing import assert_queries

with assert_queries(max_queries=10):
    response = client.get("/dashboard/")
```

If 16 queries occur:

``` text
QueryWatchError

Query budget exceeded.

Expected: <= 10
Actual: 16
Exceeded by: 6
```

The exception should expose useful structured information
programmatically.

Example conceptual API:

``` python
error.actual_queries
error.max_queries
error.findings
```

Do not rely only on formatted strings.

------------------------------------------------------------------------

# 22. Query Budget Design

The budget mechanism should eventually support:

``` python
assert_queries(max_queries=10)
```

Later possibilities:

``` python
assert_queries(
    max_queries=10,
    max_total_time_ms=100,
)
```

Do not implement the second form in v0.1 unless the design remains
clean.

------------------------------------------------------------------------

# 23. Findings Data Model

Do not use Django models.

Use Python data structures.

Conceptual:

``` python
Finding(
    rule="slow-query",
    severity="warning",
    title="Slow query",
    message="...",
    evidence={...},
    suggestion="...",
)
```

Suggested fields:

``` text
rule
severity
title
message
evidence
suggestion
fingerprint
```

Optional:

``` text
source_location
```

Add source location only when it can be obtained reliably.

------------------------------------------------------------------------

# 24. Severity

Use only:

``` text
info
warning
error
```

Suggested semantics:

### info

Potential optimization or informational observation.

### warning

Suspicious behavior that deserves developer attention.

### error

A configured test/performance requirement was violated.

Do not assign severity based on arbitrary business assumptions.

------------------------------------------------------------------------

# 25. Configuration

Create a central configuration layer.

Initial settings:

``` python
QUERYWATCH_ENABLED = True

QUERYWATCH_SLOW_QUERY_MS = 100

QUERYWATCH_DUPLICATE_THRESHOLD = 3

QUERYWATCH_MAX_QUERIES = None
```

Potential future settings:

``` text
QUERYWATCH_CAPTURE_STACKTRACE
QUERYWATCH_NPLUS1_THRESHOLD
QUERYWATCH_OUTPUT
QUERYWATCH_FAIL_ON
```

Do not add settings until functionality requires them.

Use Django settings safely.

Do not mutate the user's settings.

------------------------------------------------------------------------

# 26. Middleware

Target:

``` python
querywatch.middleware.QueryWatchMiddleware
```

Responsibilities:

1.  Start a request-level QueryWatch session.
2.  Attach query instrumentation to relevant database connections.
3.  Execute downstream middleware/view.
4.  Stop instrumentation.
5.  Analyze captured queries.
6.  Produce configured output.
7.  Never interfere with the application's normal response/error
    behavior unless explicitly configured to fail.

Important:

Do not make QueryWatch middleware silently change HTTP status codes.

If a database exception occurs in the application, preserve normal
Django behavior.

------------------------------------------------------------------------

# 27. Multiple Databases

Django supports multiple database connections.

QueryWatch should not assume:

``` python
connections["default"]
```

is the only database.

Initial implementation should be designed so that connection aliases can
be tracked.

Example:

``` text
default
analytics
replica
```

Each `QueryRecord` should retain the database alias.

A later configuration can control which aliases are monitored.

------------------------------------------------------------------------

# 28. Async Considerations

Django supports asynchronous request handling.

Do not assume that thread-local state is sufficient for all execution
paths.

Design request/session state carefully.

For v0.1:

-   make the synchronous path correct
-   avoid unsafe global state
-   avoid mutable module-level collector state
-   use context-local state where appropriate

Do not fake async support.

If a feature cannot safely support async in v0.1, document the
limitation and add tests before claiming support.

------------------------------------------------------------------------

# 29. Security and Privacy

QueryWatch handles SQL and potentially query parameters.

Therefore:

-   never send captured SQL to an external service
-   never send data to OpenAI or another AI service
-   never write parameters to logs by default
-   avoid exposing secrets
-   avoid printing sensitive parameter values
-   do not store captured queries permanently in v0.1

The default output should favor SQL structure over sensitive values.

If parameters are included in a future report, they should be explicitly
controlled.

------------------------------------------------------------------------

# 30. Console Reporter

The console reporter should be readable without third-party UI
libraries.

Example:

``` text
QueryWatch
────────────────────────────────

Request: GET /orders/

Queries: 27
Total DB time: 84.3ms

Findings
────────────────────────────────

WARNING  Possible N+1
19 similar queries detected.

WARNING  Slow query
183ms > 100ms

INFO  Duplicate query
7 executions
```

Keep it simple.

Avoid introducing Rich/Textual/etc. unless there is a strong reason.

------------------------------------------------------------------------

# 31. JSON Reporter

JSON should be machine-readable.

Example shape:

``` json
{
  "summary": {
    "query_count": 27,
    "total_duration_ms": 84.3,
    "slow_queries": 2,
    "duplicate_groups": 4
  },
  "findings": [
    {
      "rule": "slow-query",
      "severity": "warning",
      "title": "Slow query",
      "message": "Query exceeded the configured threshold.",
      "evidence": {
        "duration_ms": 183.2,
        "threshold_ms": 100
      }
    }
  ]
}
```

The exact schema can evolve, but keep it stable once publicly
documented.

------------------------------------------------------------------------

# 32. Testing Strategy

Testing is not optional.

Every detector needs unit tests.

Minimum:

``` text
test_collector.py
test_normalizer.py
test_slow.py
test_duplicate.py
test_nplus1.py
test_budget.py
```

Also add integration tests against a minimal Django test project.

------------------------------------------------------------------------

# 33. Test Cases --- Collector

Must test:

1.  One SELECT.
2.  Multiple queries.
3.  INSERT/UPDATE/DELETE.
4.  Query duration.
5.  `many=True`.
6.  Query exception.
7.  Zero queries.
8.  Multiple database aliases where supported.
9.  Nested code paths.
10. Middleware lifecycle.

------------------------------------------------------------------------

# 34. Test Cases --- Normalizer

Test:

``` text
same query + different parameter
```

produces same fingerprint.

Also test that unrelated queries do NOT collapse together.

Test:

-   integers
-   strings
-   decimals
-   UUID-like values
-   timestamps
-   identifiers containing numbers
-   whitespace differences
-   different SQL statements

Prefer correctness over aggressive normalization.

------------------------------------------------------------------------

# 35. Test Cases --- Slow Detector

Cases:

``` text
50ms with 100ms threshold -> no finding
100ms with 100ms threshold -> finding
150ms with 100ms threshold -> finding
```

Test custom thresholds.

------------------------------------------------------------------------

# 36. Test Cases --- Duplicate Detector

Cases:

``` text
1 execution -> no duplicate
2 executions -> depending on threshold
10 executions -> finding
different normalized queries -> separate groups
```

------------------------------------------------------------------------

# 37. Test Cases --- N+1

Build realistic Django models.

Example:

``` python
class Customer(models.Model):
    name = models.CharField(max_length=100)


class Order(models.Model):
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
    )
```

Bad pattern:

``` python
orders = Order.objects.all()

for order in orders:
    print(order.customer.name)
```

Optimized pattern:

``` python
orders = Order.objects.select_related("customer")
```

The test suite should demonstrate the query-count difference.

Do not require the detector to perfectly understand the Python source in
v0.1.

------------------------------------------------------------------------

# 38. Test Cases --- Query Budget

Test:

``` text
within budget -> passes
over budget -> raises QueryWatchError
zero budget -> correct behavior
no queries -> correct behavior
```

Also test that the error exposes structured data.

------------------------------------------------------------------------

# 39. Test Isolation

Tests must not depend on:

-   developer machine configuration
-   network
-   external APIs
-   real production databases
-   environment-specific paths

Use Django's test database.

Default to SQLite for the first test suite.

Add PostgreSQL CI later.

------------------------------------------------------------------------

# 40. Code Quality

Use:

-   type hints
-   clear function names
-   small functions
-   docstrings for public APIs
-   no unnecessary abstractions
-   no dead code
-   no commented-out implementation
-   no debug prints

Avoid premature enterprise architecture.

The project is open source and should be understandable to a developer
reading it for the first time.

------------------------------------------------------------------------

# 41. Dependencies

Core runtime dependency should ideally be:

``` text
Django
```

Development dependencies can include:

``` text
pytest
pytest-django
ruff
mypy
build
```

Exact tooling can be chosen during implementation.

Do not add runtime dependencies without a concrete reason.

------------------------------------------------------------------------

# 42. Packaging

Use modern `pyproject.toml`.

Do not use:

``` text
setup.py
```

as the primary packaging configuration.

The package should use a `src/` layout.

The eventual package should build with:

``` bash
python -m build
```

and produce:

``` text
dist/
    django_querywatch-*.tar.gz
    django_querywatch-*.whl
```

------------------------------------------------------------------------

# 43. README Requirements

The README should eventually contain:

1.  Project description.
2.  Why QueryWatch exists.
3.  Installation.
4.  Quick start.
5.  Example output.
6.  Configuration.
7.  Query budget API.
8.  Supported versions.
9.  Detectors.
10. Limitations.
11. Development setup.
12. Testing.
13. Contributing.
14. License.

Do not write marketing-heavy claims.

------------------------------------------------------------------------

# 44. License

Use:

``` text
MIT License
```

unless explicitly changed later.

------------------------------------------------------------------------

# 45. Versioning

Start:

``` text
0.1.0
```

Use semantic-versioning principles.

Before `1.0.0`, public APIs may evolve.

Once a feature is documented as public, treat changes carefully.

------------------------------------------------------------------------

# 46. Changelog

Maintain:

``` text
CHANGELOG.md
```

Start with:

``` text
## [0.1.0] - Unreleased

### Added
- Initial query instrumentation
- Query timing
- Query normalization
- Duplicate detection
- Slow-query detection
- Basic N+1 detection
- Query budget testing
```

Only list features that actually exist.

------------------------------------------------------------------------

# 47. Development Workflow

Follow this order.

## Phase 1 --- Repository bootstrap

Create:

``` text
pyproject.toml
src/querywatch/
tests/
README.md
LICENSE
.gitignore
```

Make the package importable.

Run tests.

------------------------------------------------------------------------

## Phase 2 --- Minimal collector

Implement:

``` text
Django execute_wrapper
        ↓
QueryRecord
        ↓
request/session collection
```

Do not implement N+1 yet.

Write tests first.

------------------------------------------------------------------------

## Phase 3 --- Normalization

Implement:

``` text
raw SQL
   ↓
normalized SQL
   ↓
fingerprint
```

Test thoroughly.

------------------------------------------------------------------------

## Phase 4 --- Aggregation

Implement:

``` text
fingerprint
   ↓
execution count
total time
average
min
max
```

------------------------------------------------------------------------

## Phase 5 --- Detectors

Implement in this order:

1.  slow query
2.  duplicate query
3.  query count
4.  basic N+1

Do not implement all detectors simultaneously.

------------------------------------------------------------------------

## Phase 6 --- Reporting

Implement:

1.  internal report object
2.  console reporter
3.  JSON reporter

------------------------------------------------------------------------

## Phase 7 --- Testing API

Implement:

``` python
with assert_queries(max_queries=10):
    ...
```

Add tests.

------------------------------------------------------------------------

## Phase 8 --- Integration

Create a minimal Django example project.

Use it to demonstrate:

-   normal queries
-   duplicate queries
-   slow query
-   N+1
-   optimized query

------------------------------------------------------------------------

## Phase 9 --- Quality

Run:

``` bash
pytest
ruff check .
```

Add type checking if practical.

Fix all issues.

------------------------------------------------------------------------

## Phase 10 --- Packaging

Build:

``` bash
python -m build
```

Install the generated wheel into a clean environment.

Run the example project against the installed wheel.

Do not publish until this works.

------------------------------------------------------------------------

# 48. Codex Working Rules

When working on this repository, follow these rules.

## Rule 1 --- Inspect before modifying

Before changing a file, inspect the relevant existing code.

Do not overwrite files blindly.

## Rule 2 --- Small increments

Make small changes.

After each meaningful feature:

``` bash
pytest
```

## Rule 3 --- Tests before broad refactors

If adding a detector:

1.  define expected behavior
2.  write tests
3.  implement
4.  run tests
5.  refactor if necessary

## Rule 4 --- Do not invent Django APIs

Check official Django documentation/source when uncertain.

## Rule 5 --- Avoid unsupported assumptions

If Django behavior differs between 5.2, 6.0, and 6.1, test and document
the difference.

## Rule 6 --- Preserve backwards compatibility

Do not introduce unnecessary Django-version-specific behavior.

## Rule 7 --- Don't over-engineer

A working 500-line library is better than a theoretical 5,000-line
architecture.

## Rule 8 --- Don't add AI

Not in v0.1.

## Rule 9 --- Don't add a dashboard

Not in v0.1.

## Rule 10 --- Keep the package free

No paid services or infrastructure are required.

------------------------------------------------------------------------

# 49. Definition of Done --- v0.1

QueryWatch v0.1 is considered complete only when:

### Package

-   [ ] `pip install` works from a built wheel.
-   [ ] `import querywatch` works.
-   [ ] `pyproject.toml` is valid.
-   [ ] Package uses `src/` layout.

### Django integration

-   [ ] Middleware works.
-   [ ] Database queries are captured.
-   [ ] Query duration is recorded.
-   [ ] Database alias is recorded.
-   [ ] Database exceptions are not swallowed.

### Analysis

-   [ ] Query normalization works for supported cases.
-   [ ] Fingerprinting is deterministic.
-   [ ] Queries are grouped.
-   [ ] Slow queries are detected.
-   [ ] Duplicate queries are detected.
-   [ ] Query count is measured.
-   [ ] Basic possible N+1 patterns are detected.

### Reporting

-   [ ] Console report works.
-   [ ] JSON report works.

### Testing

-   [ ] Query budget API works.
-   [ ] Query budget failure exposes structured information.
-   [ ] Unit tests exist for every detector.
-   [ ] Integration tests exist.

### Quality

-   [ ] No unnecessary runtime dependencies.
-   [ ] No external service.
-   [ ] No database migrations.
-   [ ] No AI.
-   [ ] No web dashboard.
-   [ ] README explains installation and usage.
-   [ ] License exists.
-   [ ] CHANGELOG exists.

------------------------------------------------------------------------

# 50. Future Roadmap

Do not implement these now, but keep the architecture extensible enough
for them.

## v0.2

-   improved source-location reporting
-   stronger N+1 detection
-   pytest integration
-   better Django relationship suggestions
-   configurable finding thresholds
-   improved JSON schema

## v0.3

-   baseline comparison
-   performance regression detection
-   GitHub Actions integration
-   CI annotations
-   explicit EXPLAIN integration
-   richer query analysis

## v0.4+

Potential:

-   management command
-   project-wide analysis
-   query budget configuration files
-   historical local reports
-   database-specific analysis

## 1.0+

Potential:

-   stable public API
-   broader database support
-   mature CI integrations
-   optional advanced analysis

AI/LLM functionality, if ever introduced, should be optional and must
never be required by the core package.

------------------------------------------------------------------------

# 51. Important Technical Constraints

## Do not automatically run SQL twice

Captured SQL should be analyzed from the execution that already
happened.

## Do not expose raw parameters by default

Parameters can contain passwords, tokens, personal information, emails,
etc.

## Do not permanently store user queries

v0.1 is in-memory.

## Do not modify QuerySets

QueryWatch observes behavior.

It must not automatically add:

``` python
select_related()
prefetch_related()
```

to user code.

## Do not change database behavior

QueryWatch is an observer/analyzer.

It should not change transactions, isolation levels, query execution
order, or query results.

------------------------------------------------------------------------

# 52. Example Final API

The eventual developer experience should look approximately like:

``` python
# settings.py

INSTALLED_APPS = [
    ...
    "querywatch",
]

MIDDLEWARE = [
    ...
    "querywatch.middleware.QueryWatchMiddleware",
]

QUERYWATCH_SLOW_QUERY_MS = 100
QUERYWATCH_DUPLICATE_THRESHOLD = 3
```

Testing:

``` python
from querywatch.testing import assert_queries


def test_dashboard(client):
    with assert_queries(max_queries=10):
        response = client.get("/dashboard/")

    assert response.status_code == 200
```

The exact configuration API can change during implementation if a
cleaner design is discovered.

------------------------------------------------------------------------

# 53. Example Findings

## Slow query

``` text
WARNING Slow query

Query duration: 382.1ms
Threshold: 100ms

Database: default
```

## Duplicate query

``` text
INFO Duplicate query

The same query pattern was executed 12 times.

Total duration: 34.2ms
Average duration: 2.85ms
```

## Possible N+1

``` text
WARNING Possible N+1 query pattern

A query pattern was executed 21 times
with different parameter values.

This may indicate repeated relationship
access inside a loop.

Possible improvements:
- select_related()
- prefetch_related()
```

## Query budget

``` text
ERROR Query budget exceeded

Expected: <= 10
Actual: 17
Exceeded by: 7
```

------------------------------------------------------------------------

# 54. First Coding Task

Do NOT immediately implement every feature in this document.

Start with only:

## Task 1

Create the package skeleton:

``` text
pyproject.toml
src/querywatch/__init__.py
src/querywatch/apps.py
tests/
README.md
LICENSE
.gitignore
```

## Task 2

Configure the package for:

``` text
Python >=3.12
Django >=5.2
```

with an appropriate upper compatibility bound only if justified by
implementation/testing.

## Task 3

Create a minimal Django test setup.

## Task 4

Create a minimal `QueryRecord` representation.

## Task 5

Implement the smallest possible database collector using Django's
`execute_wrapper()`.

## Task 6

Write tests proving that one Django query is captured.

## Task 7

Run the test suite.

Only after Task 7 passes should implementation continue to
normalization.

------------------------------------------------------------------------

# 55. Codex Execution Instruction

When starting work from this document:

1.  Inspect the repository.
2.  Determine whether files already exist.
3.  Do not delete existing work without reason.
4.  Create the minimal package skeleton.
5.  Install development dependencies in the project's environment.
6.  Implement only the first milestone.
7.  Run tests.
8.  Fix failures.
9.  Show a concise summary of:
    -   files created/changed
    -   tests run
    -   current status
    -   next recommended task
10. Stop after the milestone unless explicitly asked to continue.

Do not generate the entire project in one uncontrolled pass.

The objective is a real, tested open-source package, not a large amount
of generated code.

------------------------------------------------------------------------

# 56. Source References

Use official Django documentation as the primary authority for Django
APIs:

-   Django database instrumentation:
    https://docs.djangoproject.com/en/6.1/topics/db/instrumentation/

-   Django database optimization:
    https://docs.djangoproject.com/en/6.1/topics/db/optimization/

-   Django QuerySet API:
    https://docs.djangoproject.com/en/6.1/ref/models/querysets/

-   Django installation/Python compatibility:
    https://docs.djangoproject.com/en/6.1/faq/install/

-   Django 6.0 release notes:
    https://docs.djangoproject.com/en/6.0/releases/6.0/

-   Django 6.1 release notes:
    https://docs.djangoproject.com/en/6.1/releases/6.1/

Third-party tools researched for differentiation:

-   Django Debug Toolbar:
    https://github.com/django-debug-toolbar/django-debug-toolbar

-   Django Silk: https://github.com/jazzband/django-silk

-   django-querycount:
    https://github.com/bradmontgomery/django-querycount

-   django-nplus1: https://pypi.org/project/django-nplus1/

-   django-query-profiler:
    https://pypi.org/project/django-query-profiler/

These projects are references for ecosystem awareness, not
implementation templates.

------------------------------------------------------------------------

# 57. Final Product Principle

Keep this sentence in mind throughout development:

> QueryWatch should not merely tell a Django developer what queries
> happened. It should help them understand which query behavior deserves
> attention, why it may matter, and what they can investigate next.

Build the smallest reliable version of that idea first.
