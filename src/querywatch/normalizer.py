"""Conservative SQL normalization and deterministic fingerprinting."""

from __future__ import annotations

from hashlib import sha256
import re


_DOLLAR_QUOTE = re.compile(r"\$[A-Za-z_][A-Za-z0-9_]*\$|\$\$")


def normalize_sql(sql: str) -> str:
    """Return a conservative, whitespace-normalized SQL representation.

    QueryWatch relies on Django's parameterized SQL, so this function does
    not replace literal values. It only folds whitespace outside quoted
    strings and identifiers. Queries containing comments or PostgreSQL
    dollar-quoted strings are returned unchanged (apart from edge whitespace)
    because safely parsing those forms needs a full SQL parser.
    """
    stripped_sql = sql.strip()
    if _contains_unsupported_construct(stripped_sql):
        return stripped_sql

    normalized: list[str] = []
    quote: str | None = None
    pending_whitespace = False

    for character in stripped_sql:
        if quote is not None:
            normalized.append(character)
            if character == quote:
                quote = None
            continue

        if character in {"'", '"'}:
            if pending_whitespace and normalized:
                normalized.append(" ")
            pending_whitespace = False
            normalized.append(character)
            quote = character
        elif character.isspace():
            pending_whitespace = True
        else:
            if pending_whitespace and normalized:
                normalized.append(" ")
            pending_whitespace = False
            normalized.append(character)

    return "".join(normalized)


def fingerprint_sql(sql: str) -> str:
    """Return a stable SHA-256 fingerprint of normalized SQL."""
    return fingerprint_normalized_sql(normalize_sql(sql))


def fingerprint_normalized_sql(normalized_sql: str) -> str:
    """Return a stable SHA-256 fingerprint of already-normalized SQL."""
    return sha256(normalized_sql.encode("utf-8")).hexdigest()


def _contains_unsupported_construct(sql: str) -> bool:
    """Identify SQL forms this small normalizer intentionally avoids parsing."""
    return "--" in sql or "/*" in sql or _DOLLAR_QUOTE.search(sql) is not None
