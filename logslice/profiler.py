"""Profile a log file: line count, byte size, time range, and lines-per-second rate."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Callable, Iterable, Optional

from logslice.slicer import default_line_parser


@dataclass
class LogProfile:
    total_lines: int = 0
    total_bytes: int = 0
    first_timestamp: Optional[datetime] = None
    last_timestamp: Optional[datetime] = None
    parse_errors: int = 0
    level_counts: dict = field(default_factory=dict)

    @property
    def duration(self) -> Optional[timedelta]:
        if self.first_timestamp and self.last_timestamp:
            return self.last_timestamp - self.first_timestamp
        return None

    @property
    def lines_per_second(self) -> Optional[float]:
        d = self.duration
        if d is None:
            return None
        secs = d.total_seconds()
        return self.total_lines / secs if secs > 0 else None


def profile_lines(
    lines: Iterable[str],
    line_parser: Callable[[str], Optional[datetime]] = default_line_parser,
) -> LogProfile:
    """Consume an iterable of log lines and return a LogProfile."""
    prof = LogProfile()
    for line in lines:
        prof.total_lines += 1
        prof.total_bytes += len(line.encode())
        ts = line_parser(line)
        if ts is None:
            prof.parse_errors += 1
        else:
            if prof.first_timestamp is None:
                prof.first_timestamp = ts
            prof.last_timestamp = ts
        # best-effort level extraction
        upper = line.upper()
        for lvl in ("ERROR", "WARN", "WARNING", "INFO", "DEBUG", "CRITICAL"):
            if lvl in upper:
                key = "WARN" if lvl == "WARNING" else lvl
                prof.level_counts[key] = prof.level_counts.get(key, 0) + 1
                break
    return prof


def profile_file(
    path: str,
    line_parser: Callable[[str], Optional[datetime]] = default_line_parser,
) -> LogProfile:
    """Open *path* and profile it, also recording total file bytes from the OS."""
    with open(path, "r", errors="replace") as fh:
        prof = profile_lines(fh, line_parser)
    # use OS size as authoritative byte count
    prof.total_bytes = os.path.getsize(path)
    return prof
