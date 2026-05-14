"""Context lines support: include N lines before/after matching time-bounded slice."""

from collections import deque
from typing import Iterable, Iterator


def with_context(
    lines: Iterable[str],
    before: int = 0,
    after: int = 0,
) -> Iterator[str]:
    """Yield lines from *lines*, padding each end with up to *before* lines
    of leading context and *after* lines of trailing context.

    Duplicate lines that fall into both a trailing-context window and the
    next match's leading-context window are emitted only once.
    """
    if before < 0 or after < 0:
        raise ValueError("before and after must be non-negative integers")

    if before == 0 and after == 0:
        yield from lines
        return

    # Buffer holds (line, is_slice_line) tuples
    pre_buf: deque[str] = deque(maxlen=before)
    post_buf: list[str] = []
    pending_after: int = 0
    emitted_indices: set[int] = set()
    all_lines: list[str] = list(lines)

    i = 0
    while i < len(all_lines):
        line = all_lines[i]
        # Slice lines are all lines passed in; context wraps the whole block
        # Emit pre-context
        if before > 0:
            start = max(0, i - before)
            for j in range(start, i):
                if j not in emitted_indices:
                    emitted_indices.add(j)
                    yield all_lines[j]
        if i not in emitted_indices:
            emitted_indices.add(i)
            yield line
        # Emit post-context
        if after > 0:
            end = min(len(all_lines), i + after + 1)
            for j in range(i + 1, end):
                if j not in emitted_indices:
                    emitted_indices.add(j)
                    yield all_lines[j]
        i += 1


def context_window(
    lines: Iterable[str],
    predicate,
    before: int = 0,
    after: int = 0,
) -> Iterator[str]:
    """Yield lines that satisfy *predicate*, plus up to *before*/*after*
    surrounding context lines.  Overlapping windows are merged."""
    if before < 0 or after < 0:
        raise ValueError("before and after must be non-negative integers")

    all_lines: list[str] = list(lines)
    emitted: set[int] = set()

    for i, line in enumerate(all_lines):
        if predicate(line):
            start = max(0, i - before)
            end = min(len(all_lines), i + after + 1)
            for j in range(start, end):
                if j not in emitted:
                    emitted.add(j)
                    yield all_lines[j]
