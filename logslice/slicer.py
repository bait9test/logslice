"""Core log slicing logic: extracts lines within a time range from a log file."""

import os
from datetime import datetime
from typing import Callable, Iterator, Optional

from logslice.binary_search import binary_search_offset
from logslice.timestamp_parser import parse_timestamp


def default_line_parser(line: str) -> Optional[datetime]:
    """Try to parse a timestamp from the beginning of a log line."""
    if not line:
        return None
    # take up to the first 40 chars as a candidate timestamp prefix
    candidate = line[:40].split(" ")[0] if " " in line[:40] else line[:40]
    try:
        return parse_timestamp(candidate)
    except Exception:
        # try with first two space-separated tokens (e.g. "2024-01-01 12:00:00")
        parts = line.split(" ")
        if len(parts) >= 2:
            try:
                return parse_timestamp(parts[0] + " " + parts[1])
            except Exception:
                pass
    return None


def slice_log(
    filepath: str,
    start: datetime,
    end: datetime,
    line_parser: Callable[[str], Optional[datetime]] = default_line_parser,
    encoding: str = "utf-8",
) -> Iterator[str]:
    """
    Yield log lines whose timestamps fall within [start, end] (inclusive).

    Uses binary search to locate the start offset, then streams forward
    until the end boundary is exceeded.
    """
    file_size = os.path.getsize(filepath)
    if file_size == 0:
        return

    with open(filepath, "rb") as fh:
        start_offset = binary_search_offset(fh, start, line_parser, 0, file_size)

        fh.seek(start_offset)
        for raw_line in fh:
            line = raw_line.decode(encoding, errors="replace").rstrip("\n")
            ts = line_parser(line)
            if ts is None:
                # include unparseable lines that follow a valid in-range line
                yield line
                continue
            if ts > end:
                break
            if ts >= start:
                yield line
