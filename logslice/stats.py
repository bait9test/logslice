"""Compute basic statistics over a log slice."""

from collections import Counter
from dataclasses import dataclass, field
from typing import Iterable, Optional

from logslice.filters import _line_level


@dataclass
class SliceStats:
    total_lines: int = 0
    level_counts: Counter = field(default_factory=Counter)
    first_timestamp: Optional[str] = None
    last_timestamp: Optional[str] = None
    bytes_read: int = 0

    def as_dict(self) -> dict:
        return {
            "total_lines": self.total_lines,
            "level_counts": dict(self.level_counts),
            "first_timestamp": self.first_timestamp,
            "last_timestamp": self.last_timestamp,
            "bytes_read": self.bytes_read,
        }


def collect_stats(lines: Iterable[str]) -> SliceStats:
    """Iterate over lines and collect statistics without storing them."""
    stats = SliceStats()

    for line in lines:
        stats.total_lines += 1
        stats.bytes_read += len(line.encode("utf-8", errors="replace"))

        level = _line_level(line)
        if level:
            stats.level_counts[level] += 1
        else:
            stats.level_counts["UNKNOWN"] += 1

        ts_part = line.split(" ", 1)[0].strip()
        if ts_part:
            if stats.first_timestamp is None:
                stats.first_timestamp = ts_part
            stats.last_timestamp = ts_part

    return stats


def summarise(stats: SliceStats) -> str:
    """Return a human-readable summary string."""
    lines = [
        f"Lines     : {stats.total_lines}",
        f"Bytes     : {stats.bytes_read}",
        f"First ts  : {stats.first_timestamp or 'n/a'}",
        f"Last ts   : {stats.last_timestamp or 'n/a'}",
        "Levels    :",
    ]
    for level, count in sorted(stats.level_counts.items()):
        lines.append(f"  {level:<10} {count}")
    return "\n".join(lines)
