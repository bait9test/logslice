"""Build and query a lightweight byte-offset index for large log files.

The index maps a sampled set of timestamps to their byte offsets so that
binary search can start from a much closer position instead of always
beginning at offset 0 or EOF.
"""
from __future__ import annotations

import bisect
from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable, Iterable, List, Optional, Tuple

from logslice.timestamp_parser import parse_timestamp


@dataclass
class LogIndex:
    """Sorted list of (timestamp, byte_offset) pairs."""
    entries: List[Tuple[datetime, int]] = field(default_factory=list)

    def add(self, ts: datetime, offset: int) -> None:
        """Append an entry; caller must ensure entries stay sorted."""
        self.entries.append((ts, offset))

    def nearest_offset_before(self, ts: datetime) -> int:
        """Return the largest byte offset whose timestamp is <= *ts*.

        Returns 0 when no entry precedes *ts*.
        """
        if not self.entries:
            return 0
        keys = [e[0] for e in self.entries]
        pos = bisect.bisect_right(keys, ts)
        if pos == 0:
            return 0
        return self.entries[pos - 1][1]

    def __len__(self) -> int:  # pragma: no cover
        return len(self.entries)


def build_index(
    lines: Iterable[str],
    every_n: int = 1000,
    line_parser: Optional[Callable[[str], Optional[datetime]]] = None,
    *,
    start_offset: int = 0,
) -> LogIndex:
    """Scan *lines* and record a timestamp→offset entry every *every_n* lines.

    *start_offset* is the byte offset of the first line in the source file;
    subsequent offsets are accumulated from ``len(line.encode())``.  This is
    an approximation suitable for ASCII / UTF-8 logs.
    """
    if every_n < 1:
        raise ValueError("every_n must be >= 1")

    parser = line_parser or _default_parser
    index = LogIndex()
    offset = start_offset

    for lineno, line in enumerate(lines):
        if lineno % every_n == 0:
            ts = parser(line)
            if ts is not None:
                index.add(ts, offset)
        offset += len(line.encode("utf-8", errors="replace"))

    return index


def _default_parser(line: str) -> Optional[datetime]:
    try:
        return parse_timestamp(line.split()[0]) if line.strip() else None
    except Exception:
        return None
