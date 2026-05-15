"""Normalize log lines to a consistent format."""

from __future__ import annotations

import re
from typing import Callable, Iterable, Iterator

# Patterns that map messy level strings to canonical names
_LEVEL_ALIASES: dict[str, str] = {
    "warn": "WARNING",
    "warning": "WARNING",
    "err": "ERROR",
    "error": "ERROR",
    "crit": "CRITICAL",
    "critical": "CRITICAL",
    "info": "INFO",
    "information": "INFO",
    "dbg": "DEBUG",
    "debug": "DEBUG",
    "trace": "TRACE",
}

_LEVEL_RE = re.compile(
    r"\b(" + "|".join(re.escape(k) for k in _LEVEL_ALIASES) + r")\b",
    re.IGNORECASE,
)


def normalize_level(line: str) -> str:
    """Replace non-canonical level tokens with their canonical equivalents."""

    def _replace(m: re.Match) -> str:  # type: ignore[type-arg]
        return _LEVEL_ALIASES[m.group(0).lower()]

    return _LEVEL_RE.sub(_replace, line)


def normalize_whitespace(line: str) -> str:
    """Collapse runs of spaces/tabs to a single space, preserving newline."""
    stripped = line.rstrip("\n")
    normalized = re.sub(r"[ \t]+", " ", stripped).strip()
    return normalized + "\n" if line.endswith("\n") else normalized


def normalize_line(line: str, *, fix_level: bool = True, fix_whitespace: bool = True) -> str:
    """Apply all enabled normalization steps to a single line."""
    if fix_whitespace:
        line = normalize_whitespace(line)
    if fix_level:
        line = normalize_level(line)
    return line


def normalize_lines(
    lines: Iterable[str],
    *,
    fix_level: bool = True,
    fix_whitespace: bool = True,
    transform: Callable[[str], str] | None = None,
) -> Iterator[str]:
    """Yield normalized versions of each line.

    Args:
        lines: Input lines.
        fix_level: Canonicalize log level tokens.
        fix_whitespace: Collapse redundant whitespace.
        transform: Optional extra transform applied after built-in steps.
    """
    for line in lines:
        result = normalize_line(line, fix_level=fix_level, fix_whitespace=fix_whitespace)
        if transform is not None:
            result = transform(result)
        yield result
