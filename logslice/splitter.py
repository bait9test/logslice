"""Split a log stream into chunks based on a time interval or line count."""

from __future__ import annotations

from datetime import timedelta
from typing import Callable, Iterable, Iterator, List, Optional

from logslice.timestamp_parser import parse_timestamp


def _default_key(line: str) -> Optional[object]:
    """Return a parsed timestamp from the line, or None."""
    return parse_timestamp(line)


def split_by_count(
    lines: Iterable[str],
    chunk_size: int,
) -> Iterator[List[str]]:
    """Yield successive non-overlapping chunks of *chunk_size* lines.

    Args:
        lines: Iterable of log lines.
        chunk_size: Maximum number of lines per chunk.  Must be >= 1.

    Yields:
        Lists of lines, each at most *chunk_size* long.
    """
    if chunk_size < 1:
        raise ValueError(f"chunk_size must be >= 1, got {chunk_size}")

    chunk: List[str] = []
    for line in lines:
        chunk.append(line)
        if len(chunk) == chunk_size:
            yield chunk
            chunk = []
    if chunk:
        yield chunk


def split_by_time(
    lines: Iterable[str],
    interval: timedelta,
    line_parser: Callable[[str], Optional[object]] = _default_key,
) -> Iterator[List[str]]:
    """Yield chunks of lines whose timestamps fall within *interval* windows.

    Lines without a parseable timestamp are appended to the current chunk.

    Args:
        lines: Iterable of log lines.
        interval: Duration of each time window.
        line_parser: Callable that returns a datetime (or compatible) from a
            line, or None if the line has no timestamp.

    Yields:
        Lists of lines belonging to the same time window.
    """
    if interval.total_seconds() <= 0:
        raise ValueError("interval must be positive")

    chunk: List[str] = []
    window_start = None

    for line in lines:
        ts = line_parser(line)
        if ts is not None:
            if window_start is None:
                window_start = ts
            elif ts - window_start >= interval:  # type: ignore[operator]
                if chunk:
                    yield chunk
                    chunk = []
                window_start = ts
        chunk.append(line)

    if chunk:
        yield chunk
