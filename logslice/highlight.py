"""Terminal colour highlighting for log lines."""

from __future__ import annotations

import re
from typing import Iterable, Iterator

# ANSI escape codes
_RESET = "\033[0m"
_COLOURS = {
    "red": "\033[31m",
    "yellow": "\033[33m",
    "green": "\033[32m",
    "cyan": "\033[36m",
    "magenta": "\033[35m",
    "bold": "\033[1m",
}

_LEVEL_COLOURS = {
    "error": _COLOURS["red"],
    "critical": _COLOURS["red"] + _COLOURS["bold"],
    "warning": _COLOURS["yellow"],
    "warn": _COLOURS["yellow"],
    "info": _COLOURS["green"],
    "debug": _COLOURS["cyan"],
}


def _colour(text: str, code: str) -> str:
    return f"{code}{text}{_RESET}"


def highlight_term(line: str, term: str, colour: str = "magenta") -> str:
    """Wrap every occurrence of *term* in *line* with the given colour."""
    if not term:
        return line
    code = _COLOURS.get(colour, _COLOURS["magenta"])
    escaped = re.escape(term)
    return re.sub(
        f"({escaped})",
        lambda m: _colour(m.group(1), code),
        line,
        flags=re.IGNORECASE,
    )


def highlight_level(line: str) -> str:
    """Colour the whole line based on the log level found inside it."""
    lower = line.lower()
    for level, code in _LEVEL_COLOURS.items():
        if level in lower:
            return _colour(line.rstrip("\n"), code) + ("\n" if line.endswith("\n") else "")
    return line


def highlight_lines(
    lines: Iterable[str],
    *,
    term: str | None = None,
    by_level: bool = False,
    colour: str = "magenta",
) -> Iterator[str]:
    """Apply highlighting to an iterable of log lines.

    Parameters
    ----------
    lines:    source lines (may be a generator)
    term:     optional search term to highlight within each line
    by_level: if True, colour the entire line according to its log level
    colour:   colour name used for *term* highlighting
    """
    for line in lines:
        if by_level:
            line = highlight_level(line)
        if term:
            line = highlight_term(line, term, colour)
        yield line
