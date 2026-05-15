"""Diff two log streams, yielding lines unique to each or common to both."""
from __future__ import annotations

from typing import Iterable, Iterator, Literal

Mode = Literal["left", "right", "common", "all"]


def _key(line: str) -> str:
    """Strip leading/trailing whitespace for comparison purposes."""
    return line.rstrip("\n")


def diff_logs(
    left: Iterable[str],
    right: Iterable[str],
    mode: Mode = "all",
) -> Iterator[tuple[str, str]]:
    """Compare two log streams line by line (set-based).

    Yields ``(tag, line)`` tuples where *tag* is one of:
      - ``"<"``  line only in *left*
      - ``">"``  line only in *right*
      - ``"="``  line present in both

    Parameters
    ----------
    left, right:
        Iterables of log lines.
    mode:
        ``"left"``   – only lines unique to left
        ``"right"``  – only lines unique to right
        ``"common"`` – only shared lines
        ``"all"``    – everything (default)
    """
    left_set = {_key(l) for l in left}
    right_set = {_key(r) for r in right}

    common = left_set & right_set
    only_left = left_set - right_set
    only_right = right_set - left_set

    results: list[tuple[str, str]] = []

    if mode in ("left", "all"):
        results.extend(("<", ln + "\n") for ln in sorted(only_left))
    if mode in ("right", "all"):
        results.extend((">" , ln + "\n") for ln in sorted(only_right))
    if mode in ("common", "all"):
        results.extend(("=", ln + "\n") for ln in sorted(common))

    yield from results


def diff_summary(left: Iterable[str], right: Iterable[str]) -> dict[str, int]:
    """Return counts of left-only, right-only, and common lines."""
    left_set = {_key(l) for l in left}
    right_set = {_key(r) for r in right}
    return {
        "left_only": len(left_set - right_set),
        "right_only": len(right_set - left_set),
        "common": len(left_set & right_set),
    }
