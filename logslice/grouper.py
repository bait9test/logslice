"""Group log lines by a key derived from each line."""
from __future__ import annotations

from collections import defaultdict
from typing import Callable, Dict, Iterable, Iterator, List, Tuple


def _default_key(line: str) -> str:
    """Use the first whitespace-separated token (timestamp) as the group key."""
    parts = line.split(None, 1)
    return parts[0] if parts else ""


def group_by(
    lines: Iterable[str],
    key_fn: Callable[[str], str] = _default_key,
) -> Dict[str, List[str]]:
    """Collect *lines* into a dict keyed by *key_fn(line)*.

    Lines whose key is an empty string are stored under the empty-string key.
    """
    groups: Dict[str, List[str]] = defaultdict(list)
    for line in lines:
        groups[key_fn(line)].append(line)
    return dict(groups)


def iter_groups(
    lines: Iterable[str],
    key_fn: Callable[[str], str] = _default_key,
) -> Iterator[Tuple[str, List[str]]]:
    """Yield *(key, [lines])* pairs in the order keys are first seen."""
    seen_order: List[str] = []
    groups: Dict[str, List[str]] = defaultdict(list)
    for line in lines:
        k = key_fn(line)
        if k not in groups:
            seen_order.append(k)
        groups[k].append(line)
    for k in seen_order:
        yield k, groups[k]


def group_counts(
    lines: Iterable[str],
    key_fn: Callable[[str], str] = _default_key,
) -> Dict[str, int]:
    """Return a dict mapping each key to the number of lines in that group."""
    counts: Dict[str, int] = defaultdict(int)
    for line in lines:
        counts[key_fn(line)] += 1
    return dict(counts)


def top_groups(
    lines: Iterable[str],
    n: int = 10,
    key_fn: Callable[[str], str] = _default_key,
) -> List[Tuple[str, int]]:
    """Return the *n* most frequent groups as *(key, count)* pairs, descending."""
    if n < 1:
        raise ValueError("n must be >= 1")
    counts = group_counts(lines, key_fn=key_fn)
    return sorted(counts.items(), key=lambda kv: kv[1], reverse=True)[:n]
