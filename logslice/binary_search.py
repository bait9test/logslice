"""Binary search utilities for finding timestamp boundaries in log files."""

import os
from typing import Optional, Callable
from datetime import datetime


def find_line_start(f, pos: int) -> int:
    """Given a file position, seek backwards to find the start of the current line."""
    if pos == 0:
        return 0
    f.seek(pos)
    # Move back until we find a newline or reach the beginning
    while pos > 0:
        pos -= 1
        f.seek(pos)
        char = f.read(1)
        if char == b'\n':
            return pos + 1
    return 0


def read_line_at(f, pos: int) -> Optional[bytes]:
    """Read a single line starting at or after the given file position."""
    start = find_line_start(f, pos)
    f.seek(start)
    line = f.readline()
    return line if line else None


def binary_search_offset(
    f,
    target: datetime,
    file_size: int,
    parse_line_ts: Callable[[bytes], Optional[datetime]],
    find_first: bool = True,
) -> int:
    """
    Binary search a log file for the offset of the first (or last) line
    whose timestamp is >= (or <=) the target datetime.

    Args:
        f: Open binary file handle.
        target: The datetime boundary to search for.
        file_size: Total size of the file in bytes.
        parse_line_ts: Callable that extracts a datetime from a raw log line bytes.
        find_first: If True, find the first line >= target. If False, find last line <= target.

    Returns:
        File offset (int) of the matched line, or file_size if not found.
    """
    lo, hi = 0, file_size
    result = file_size if find_first else 0

    while lo < hi:
        mid = (lo + hi) // 2
        line = read_line_at(f, mid)
        if not line:
            break

        ts = parse_line_ts(line)
        if ts is None:
            # Can't parse this line; nudge forward
            lo = mid + len(line)
            continue

        if find_first:
            if ts < target:
                lo = mid + 1
            else:
                result = find_line_start(f, mid)
                hi = mid
        else:
            if ts <= target:
                result = find_line_start(f, mid)
                lo = mid + 1
            else:
                hi = mid

    return result
