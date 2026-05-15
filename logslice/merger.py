"""Merge multiple sorted log streams into a single time-ordered sequence."""

from __future__ import annotations

import heapq
from typing import Callable, Iterable, Iterator, List, Optional, Tuple

from logslice.timestamp_parser import parse_timestamp


def _default_key(line: str) -> Optional[float]:
    """Return a float epoch from the first timestamp found in *line*."""
    ts = parse_timestamp(line)
    if ts is None:
        return None
    return ts.timestamp()


def merge_logs(
    streams: List[Iterable[str]],
    key: Callable[[str], Optional[float]] = _default_key,
    drop_unparseable: bool = False,
) -> Iterator[str]:
    """Yield lines from *streams* in ascending timestamp order.

    Lines whose timestamp cannot be parsed are placed at the front of the
    output (key treated as -inf) unless *drop_unparseable* is True, in which
    case they are silently discarded.

    Parameters
    ----------
    streams:
        Any number of iterables that each yield log lines.
    key:
        Callable that maps a line to a comparable float (epoch seconds).
        Return ``None`` to signal an unparseable line.
    drop_unparseable:
        When True, lines with no parseable timestamp are dropped entirely.
    """
    # heap entries: (sort_key, stream_index, line)
    heap: List[Tuple[float, int, str]] = []

    iters = [iter(s) for s in streams]

    def _push(stream_idx: int) -> None:
        try:
            line = next(iters[stream_idx])
        except StopIteration:
            return
        k = key(line)
        if k is None:
            if drop_unparseable:
                # try the next line from the same stream
                _push(stream_idx)
                return
            k = float("-inf")
        heapq.heappush(heap, (k, stream_idx, line))

    for idx in range(len(iters)):
        _push(idx)

    while heap:
        _, stream_idx, line = heapq.heappop(heap)
        yield line
        _push(stream_idx)
