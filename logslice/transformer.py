"""Line transformation utilities — apply field-level mutations to log lines."""

from __future__ import annotations

import re
from typing import Callable, Iterable, Iterator

# A transformer takes a line and returns a (possibly modified) line.
LineTransformer = Callable[[str], str]


def uppercase_level(line: str) -> str:
    """Uppercase common level tokens (debug, info, warn, error, critical)."""
    return re.sub(
        r'\b(debug|info|warn(?:ing)?|error|critical)\b',
        lambda m: m.group(0).upper(),
        line,
        flags=re.IGNORECASE,
    )


def strip_ansi(line: str) -> str:
    """Remove ANSI escape sequences from a line."""
    return re.sub(r'\x1b\[[0-9;]*m', '', line)


def replace_field(pattern: str, replacement: str, *, flags: int = 0) -> LineTransformer:
    """Return a transformer that substitutes *pattern* with *replacement*."""
    compiled = re.compile(pattern, flags)

    def _transform(line: str) -> str:
        return compiled.sub(replacement, line)

    return _transform


def prepend_text(prefix: str) -> LineTransformer:
    """Return a transformer that prepends *prefix* to every line."""

    def _transform(line: str) -> str:
        newline = '\n' if line.endswith('\n') else ''
        body = line.rstrip('\n')
        return f"{prefix}{body}{newline}"

    return _transform


def append_text(suffix: str) -> LineTransformer:
    """Return a transformer that appends *suffix* before the trailing newline."""

    def _transform(line: str) -> str:
        newline = '\n' if line.endswith('\n') else ''
        body = line.rstrip('\n')
        return f"{body}{suffix}{newline}"

    return _transform


def chain(*transformers: LineTransformer) -> LineTransformer:
    """Compose multiple transformers left-to-right into a single transformer."""

    def _transform(line: str) -> str:
        for t in transformers:
            line = t(line)
        return line

    return _transform


def transform_lines(
    lines: Iterable[str],
    *transformers: LineTransformer,
) -> Iterator[str]:
    """Apply one or more transformers to each line in *lines*."""
    combined = chain(*transformers)
    for line in lines:
        yield combined(line)
