"""Line sampling utilities — take every Nth line or a random fraction."""

from __future__ import annotations

import random
from typing import Iterable, Iterator


def sample_every_n(lines: Iterable[str], n: int) -> Iterator[str]:
    """Yield every *n*-th line from *lines* (1-based, so n=1 returns all).

    Args:
        lines: iterable of log lines.
        n: step size; must be >= 1.

    Raises:
        ValueError: if *n* is less than 1.
    """
    if n < 1:
        raise ValueError(f"n must be >= 1, got {n}")
    for i, line in enumerate(lines):
        if i % n == 0:
            yield line


def sample_random(
    lines: Iterable[str],
    fraction: float,
    seed: int | None = None,
) -> Iterator[str]:
    """Yield each line with probability *fraction*.

    Args:
        lines: iterable of log lines.
        fraction: probability in (0, 1] that any given line is kept.
        seed: optional RNG seed for reproducibility.

    Raises:
        ValueError: if *fraction* is not in (0, 1].
    """
    if not (0 < fraction <= 1.0):
        raise ValueError(f"fraction must be in (0, 1], got {fraction}")
    rng = random.Random(seed)
    for line in lines:
        if rng.random() < fraction:
            yield line


def sample_head(lines: Iterable[str], limit: int) -> Iterator[str]:
    """Yield at most *limit* lines from the start of *lines*.

    Args:
        lines: iterable of log lines.
        limit: maximum number of lines to return; must be >= 0.

    Raises:
        ValueError: if *limit* is negative.
    """
    if limit < 0:
        raise ValueError(f"limit must be >= 0, got {limit}")
    for i, line in enumerate(lines):
        if i >= limit:
            break
        yield line
