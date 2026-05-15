"""Deduplication utilities for log lines."""

from __future__ import annotations

import hashlib
from collections.abc import Iterable, Iterator
from typing import Callable, Optional


def _line_key(line: str) -> str:
    """Return a stable hash key for a log line, stripping the timestamp prefix.

    We drop the first token (assumed to be a timestamp) so that identical
    messages emitted at different times are still considered duplicates.
    """
    parts = line.split(None, 2)
    # If the line has at least a timestamp + level + message, use level+message.
    # Otherwise fall back to the full line.
    payload = " ".join(parts[1:]) if len(parts) >= 2 else line
    return hashlib.md5(payload.encode(), usedforsecurity=False).hexdigest()


def dedup_exact(
    lines: Iterable[str],
    key_fn: Optional[Callable[[str], str]] = None,
) -> Iterator[str]:
    """Yield each unique line exactly once (first occurrence wins).

    Args:
        lines:   Iterable of raw log lines.
        key_fn:  Optional function that maps a line to a hashable key.
                 Defaults to :func:`_line_key`.
    """
    if key_fn is None:
        key_fn = _line_key
    seen: set[str] = set()
    for line in lines:
        key = key_fn(line)
        if key not in seen:
            seen.add(key)
            yield line


def dedup_window(
    lines: Iterable[str],
    window: int = 100,
    key_fn: Optional[Callable[[str], str]] = None,
) -> Iterator[str]:
    """Yield lines that have not appeared within the last *window* lines.

    Unlike :func:`dedup_exact` this uses a bounded sliding window so memory
    usage stays constant regardless of input size.

    Args:
        lines:   Iterable of raw log lines.
        window:  Number of recent line keys to remember.
        key_fn:  Optional key function (defaults to :func:`_line_key`).
    """
    if window < 1:
        raise ValueError(f"window must be >= 1, got {window}")
    if key_fn is None:
        key_fn = _line_key

    recent: list[str] = []
    recent_set: set[str] = set()

    for line in lines:
        key = key_fn(line)
        if key not in recent_set:
            yield line
            recent.append(key)
            recent_set.add(key)
            if len(recent) > window:
                evicted = recent.pop(0)
                recent_set.discard(evicted)
