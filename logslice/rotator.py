"""Log rotation detection and segment stitching utilities."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable, Iterator, List


def _rotated_siblings(path: Path) -> List[Path]:
    """Return rotated variants of *path* sorted oldest-first.

    Looks for files named like ``app.log.1``, ``app.log.2``, … and
    ``app.log.1.gz`` alongside the base file.
    """
    parent = path.parent
    stem = path.name  # e.g. "app.log"
    siblings: List[tuple[int, Path]] = []

    for entry in parent.iterdir():
        name = entry.name
        if not name.startswith(stem + "."):
            continue
        suffix = name[len(stem) + 1:]  # "1", "2", "1.gz", …
        numeric = suffix.split(".")[0]
        if numeric.isdigit():
            siblings.append((int(numeric), entry))

    siblings.sort(key=lambda t: t[0], reverse=True)  # highest index = oldest
    return [p for _, p in siblings]


def iter_rotated_lines(
    path: str | Path,
    include_rotated: bool = True,
    opener=open,
) -> Iterator[str]:
    """Yield lines from rotated log files followed by the live file.

    Parameters
    ----------
    path:
        Path to the *current* (live) log file.
    include_rotated:
        When *False* only the live file is read (useful for testing).
    opener:
        Callable with the same signature as :func:`open`; injectable for
        tests.
    """
    base = Path(path)
    files: List[Path] = []

    if include_rotated:
        files.extend(_rotated_siblings(base))

    files.append(base)

    for fpath in files:
        try:
            with opener(fpath, "r", errors="replace") as fh:
                yield from fh
        except FileNotFoundError:
            continue


def count_rotated_segments(path: str | Path) -> int:
    """Return the number of rotated segments found next to *path*."""
    return len(_rotated_siblings(Path(path)))
