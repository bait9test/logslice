"""Tail support: stream new lines appended to a log file in real time."""

from __future__ import annotations

import time
import os
from typing import Callable, Iterator, Optional

from logslice.timestamp_parser import parse_timestamp


def _read_new_lines(fp, buf: list[str]) -> list[str]:
    """Read any newly written lines from an open file handle."""
    lines = []
    while True:
        line = fp.readline()
        if not line:
            break
        lines.append(line)
    return lines


def tail_file(
    path: str,
    *,
    poll_interval: float = 0.25,
    line_parser: Optional[Callable[[str], Optional[object]]] = None,
    stop_after: Optional[int] = None,
) -> Iterator[str]:
    """Yield lines appended to *path* after the current end-of-file.

    Parameters
    ----------
    path:           Path to the log file to watch.
    poll_interval:  Seconds between polling for new data.
    line_parser:    Optional callable; if provided, only lines for which it
                    returns a non-None value are yielded.
    stop_after:     If given, stop after yielding this many lines (useful for
                    testing / bounded streaming).
    """
    yielded = 0
    with open(path, "r", encoding="utf-8", errors="replace") as fp:
        fp.seek(0, os.SEEK_END)  # jump to current EOF
        while True:
            lines = _read_new_lines(fp, [])
            for line in lines:
                if line_parser is not None and line_parser(line) is None:
                    continue
                yield line
                yielded += 1
                if stop_after is not None and yielded >= stop_after:
                    return
            if not lines:
                time.sleep(poll_interval)
