"""Line annotation: attach sequence numbers, relative offsets, or custom tags."""
from __future__ import annotations

from typing import Callable, Iterable, Iterator


def annotate_sequence(
    lines: Iterable[str],
    start: int = 1,
    prefix: str = "",
    suffix: str = " ",
) -> Iterator[str]:
    """Prepend a monotonically increasing sequence number to each line.

    Args:
        lines:  Source lines (newlines preserved or absent — both handled).
        start:  First sequence number (default 1).
        prefix: String placed before the number (e.g. "[").
        suffix: String placed after the number before the line body.

    Yields:
        Annotated lines, each ending with '\\n'.
    """
    if start < 0:
        raise ValueError("start must be >= 0")
    for idx, line in enumerate(lines, start=start):
        body = line.rstrip("\n")
        yield f"{prefix}{idx}{suffix}{body}\n"


def annotate_tag(
    lines: Iterable[str],
    tag_fn: Callable[[str], str],
) -> Iterator[str]:
    """Prepend a custom tag returned by *tag_fn* to each line.

    Args:
        lines:  Source lines.
        tag_fn: Callable that receives the raw line and returns a tag string
                which is prepended (separated by a single space).

    Yields:
        Annotated lines, each ending with '\\n'.
    """
    for line in lines:
        body = line.rstrip("\n")
        tag = tag_fn(line)
        yield f"{tag} {body}\n"


def annotate_offset(
    lines: Iterable[str],
    byte_start: int = 0,
) -> Iterator[tuple[int, str]]:
    """Yield *(byte_offset, line)* pairs tracking the running byte position.

    Args:
        lines:      Source lines (assumed UTF-8 encoded for byte counting).
        byte_start: Initial offset (useful when slicing mid-file).

    Yields:
        Tuples of (offset_at_line_start, annotated_line_string).
    """
    if byte_start < 0:
        raise ValueError("byte_start must be >= 0")
    offset = byte_start
    for line in lines:
        yield offset, line
        offset += len(line.encode("utf-8"))
