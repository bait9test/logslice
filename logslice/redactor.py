"""redactor.py — Mask or remove sensitive patterns from log lines.

Supports built-in patterns (IP addresses, emails, UUIDs, auth tokens)
as well as custom regex patterns supplied by the caller.
"""

import re
from typing import Iterable, Iterator, List, Optional, Tuple

# ---------------------------------------------------------------------------
# Built-in patterns
# ---------------------------------------------------------------------------

#: Maps a short name to a compiled regex + replacement string.
_BUILTIN_PATTERNS: List[Tuple[str, re.Pattern, str]] = [
    (
        "email",
        re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}"),
        "[EMAIL]",
    ),
    (
        "ipv4",
        re.compile(
            r"\b(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}"
            r"(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\b"
        ),
        "[IPv4]",
    ),
    (
        "uuid",
        re.compile(
            r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}"
            r"-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b"
        ),
        "[UUID]",
    ),
    (
        "bearer",
        re.compile(r"(?i)Bearer\s+[A-Za-z0-9\-._~+/]+=*"),
        "Bearer [REDACTED]",
    ),
    (
        "basic_auth",
        re.compile(r"(?i)Basic\s+[A-Za-z0-9+/]+=*"),
        "Basic [REDACTED]",
    ),
]

_BUILTIN_NAMES = {name for name, _, _ in _BUILTIN_PATTERNS}


# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------

def redact_line(
    line: str,
    *,
    builtins: Optional[List[str]] = None,
    custom: Optional[List[Tuple[re.Pattern, str]]] = None,
) -> str:
    """Return *line* with sensitive patterns replaced.

    Parameters
    ----------
    line:
        The raw log line to process.
    builtins:
        List of built-in pattern names to apply.  Pass ``None`` (default) to
        apply **all** built-in patterns, or an empty list to skip them all.
        Valid names: ``email``, ``ipv4``, ``uuid``, ``bearer``, ``basic_auth``.
    custom:
        Extra ``(compiled_pattern, replacement)`` pairs applied after the
        built-in patterns.
    """
    # Resolve which built-ins to use.
    if builtins is None:
        active_builtins = _BUILTIN_PATTERNS
    else:
        unknown = set(builtins) - _BUILTIN_NAMES
        if unknown:
            raise ValueError(f"Unknown built-in redaction pattern(s): {unknown}")
        active_builtins = [(n, p, r) for n, p, r in _BUILTIN_PATTERNS if n in builtins]

    result = line
    for _name, pattern, replacement in active_builtins:
        result = pattern.sub(replacement, result)

    for pattern, replacement in (custom or []):
        result = pattern.sub(replacement, result)

    return result


def redact_lines(
    lines: Iterable[str],
    *,
    builtins: Optional[List[str]] = None,
    custom: Optional[List[Tuple[re.Pattern, str]]] = None,
) -> Iterator[str]:
    """Lazily apply :func:`redact_line` to each line in *lines*."""
    for line in lines:
        yield redact_line(line, builtins=builtins, custom=custom)
