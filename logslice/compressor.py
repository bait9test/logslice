"""Line-level compression utilities for logslice.

Provides helpers that compress / decompress an iterable of log lines
using gzip so callers can pipe sliced output straight to a .gz file
without buffering everything in memory.
"""

from __future__ import annotations

import gzip
import io
from typing import Iterable, Iterator


_DEFAULT_LEVEL = 6  # gzip default; good balance of speed vs size


def compress_lines(
    lines: Iterable[str],
    level: int = _DEFAULT_LEVEL,
) -> bytes:
    """Compress *lines* into a gzip byte-string.

    Each line is written as-is; a trailing newline is added only when the
    line does not already end with one.

    Args:
        lines:  Iterable of log-line strings.
        level:  gzip compression level (1-9, default 6).

    Returns:
        Compressed bytes suitable for writing to a ``.gz`` file.
    """
    buf = io.BytesIO()
    with gzip.GzipFile(fileobj=buf, mode="wb", compresslevel=level) as gz:
        for line in lines:
            if not line.endswith("\n"):
                line = line + "\n"
            gz.write(line.encode())
    return buf.getvalue()


def decompress_lines(
    data: bytes,
) -> Iterator[str]:
    """Decompress gzip *data* and yield individual log lines.

    Trailing newlines are preserved so the output is a drop-in replacement
    for reading lines from a plain text file.

    Args:
        data:  Raw gzip-compressed bytes.

    Yields:
        Decoded log-line strings (newline-terminated).
    """
    buf = io.BytesIO(data)
    with gzip.GzipFile(fileobj=buf, mode="rb") as gz:
        for raw in gz:
            yield raw.decode()


def compress_to_file(lines: Iterable[str], path: str, level: int = _DEFAULT_LEVEL) -> int:
    """Write *lines* compressed to *path*.

    Returns:
        Number of lines written.
    """
    count = 0
    with gzip.open(path, "wt", compresslevel=level) as fh:
        for line in lines:
            if not line.endswith("\n"):
                line = line + "\n"
            fh.write(line)
            count += 1
    return count


def decompress_from_file(path: str) -> Iterator[str]:
    """Yield lines from a gzip-compressed log file at *path*."""
    with gzip.open(path, "rt") as fh:
        yield from fh
