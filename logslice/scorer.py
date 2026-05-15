"""Score log lines by relevance using keyword weights."""

from __future__ import annotations

import re
from typing import Dict, Iterable, Iterator, List, Tuple


def _score_line(line: str, weights: Dict[str, float]) -> float:
    """Return the sum of weights for all terms found in *line*.

    Matching is case-insensitive.  A term may contribute its weight more
    than once if it appears multiple times.
    """
    total = 0.0
    lower = line.lower()
    for term, weight in weights.items():
        count = lower.count(term.lower())
        total += weight * count
    return total


def score_lines(
    lines: Iterable[str],
    weights: Dict[str, float],
) -> Iterator[Tuple[float, str]]:
    """Yield *(score, line)* pairs for every line in *lines*.

    Lines with a score of zero are still yielded so callers can decide
    whether to keep them.
    """
    for line in lines:
        yield _score_line(line, weights), line


def top_scored(
    lines: Iterable[str],
    weights: Dict[str, float],
    n: int = 10,
    min_score: float = 0.0,
) -> List[Tuple[float, str]]:
    """Return the top *n* lines sorted by descending score.

    Only lines with *score >= min_score* are considered.  If fewer than
    *n* qualifying lines exist, all of them are returned.
    """
    if n < 1:
        raise ValueError("n must be >= 1")

    scored = [
        (s, l)
        for s, l in score_lines(lines, weights)
        if s >= min_score
    ]
    scored.sort(key=lambda t: t[0], reverse=True)
    return scored[:n]


def filter_by_score(
    lines: Iterable[str],
    weights: Dict[str, float],
    threshold: float,
) -> Iterator[str]:
    """Yield only lines whose score meets or exceeds *threshold*."""
    if threshold < 0:
        raise ValueError("threshold must be >= 0")
    for score, line in score_lines(lines, weights):
        if score >= threshold:
            yield line
