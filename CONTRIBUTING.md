# Contributing to Django QueryWatch

Thanks for contributing. QueryWatch aims to be a small, dependable Django
developer tool, so correctness and explainability matter more than adding
features quickly.

## Development setup

Use Python 3.12 or later:

```bash
python -m pip install -e ".[dev]"
python -m ruff check .
python -m pytest
```

## Contribution guidelines

- Inspect existing behavior before changing it.
- Keep a pull request focused on one feature or fix.
- Add or update tests for every behavior change.
- Run Ruff and the entire test suite before opening a pull request.
- Do not add runtime dependencies without a concrete, documented need.
- Do not add automatic SQL re-execution, source-code rewriting, dashboards,
  cloud services, or AI dependencies to v0.1.
- Never include real query parameters, credentials, or production data in
  tests, issues, or documentation.

## Design principles

QueryWatch is an observer. It must not alter query text, parameters,
transactions, execution order, or database results. N+1 findings are
heuristics and must use cautious language such as “Possible N+1 query
pattern.”

## Reporting issues

Please include the Python version, Django version, database backend, a small
reproduction, and the expected versus observed behavior. Remove sensitive SQL
values and parameters before sharing logs.
