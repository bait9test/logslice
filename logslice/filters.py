"""Optional post-slice filtering helpers (grep, level filter, etc.)."""

import re
from typing import Callable, Iterable, Iterator, List, Optional


def grep(
    lines: Iterable[str],
    pattern: str,
    ignore_case: bool = False,
) -> Iterator[str]:
    """Yield only lines matching *pattern* (regex)."""
    flags = re.IGNORECASE if ignore_case else 0
    compiled = re.compile(pattern, flags)
    for line in lines:
        if compiled.search(line):
            yield line


# Common log level tokens ordered by severity.
_LEVELS = ["DEBUG", "INFO", "WARN", "WARNING", "ERROR", "CRITICAL", "FATAL"]
_LEVEL_RANK = {lvl: i for i, lvl in enumerate(_LEVELS)}


def _line_level(line: str) -> Optional[str]:
    """Return the log level token found in *line*, or None."""
    upper = line.upper()
    for lvl in _LEVELS:
        if lvl in upper:
            return lvl
    return None


def filter_level(
    lines: Iterable[str],
    min_level: str,
) -> Iterator[str]:
    """
    Yield lines whose log level is >= *min_level* in severity.

    Lines without a recognisable level token are always passed through.
    """
    min_rank = _LEVEL_RANK.get(min_level.upper())
    if min_rank is None:
        raise ValueError(f"Unknown log level: {min_level!r}. Choose from {_LEVELS}")

    for line in lines:
        lvl = _line_level(line)
        if lvl is None:
            yield line
            continue
        if _LEVEL_RANK.get(lvl, -1) >= min_rank:
            yield line


def pipeline(
    lines: Iterable[str],
    *filters: Callable[[Iterable[str]], Iterator[str]],
) -> Iterator[str]:
    """Chain multiple filter callables together."""
    result: Iterable[str] = lines
    for f in filters:
        result = f(result)
    return iter(result)
