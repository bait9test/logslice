"""Line truncation utilities for logslice.

Provides helpers to shorten long log lines for display purposes while
preserving the beginning and end of each line.
"""

from __future__ import annotations

from typing import Iterable, Iterator

_DEFAULT_MAX = 120
_ELLIPSIS = " ... "


def truncate_line(line: str, max_len: int = _DEFAULT_MAX) -> str:
    """Return *line* truncated to *max_len* characters.

    If the line (stripped of its trailing newline) fits within *max_len* it is
    returned unchanged.  Otherwise the middle is replaced with an ellipsis so
    that the head and tail of the line are both visible.

    Args:
        line: The raw log line (may include a trailing newline).
        max_len: Maximum length of the returned string (excluding any trailing
                 newline that was present in the original).

    Returns:
        The (possibly truncated) line.  A trailing newline is preserved if the
        original had one.
    """
    if max_len < len(_ELLIPSIS) + 2:
        raise ValueError(
            f"max_len must be at least {len(_ELLIPSIS) + 2}, got {max_len}"
        )

    trailing_newline = line.endswith("\n")
    body = line.rstrip("\n")

    if len(body) <= max_len:
        return line  # nothing to do

    keep = max_len - len(_ELLIPSIS)
    head = keep // 2
    tail = keep - head

    truncated = body[:head] + _ELLIPSIS + body[len(body) - tail :]
    return truncated + ("\n" if trailing_newline else "")


def truncate_lines(
    lines: Iterable[str],
    max_len: int = _DEFAULT_MAX,
) -> Iterator[str]:
    """Yield each line from *lines* truncated to *max_len* characters.

    Args:
        lines: Iterable of raw log lines.
        max_len: Passed through to :func:`truncate_line`.

    Yields:
        Truncated lines.
    """
    for line in lines:
        yield truncate_line(line, max_len=max_len)
