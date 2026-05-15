"""Aggregate log lines into time buckets and count occurrences."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta
from typing import Callable, Dict, Iterable, Iterator, List, Tuple


_BucketKey = str


def _floor_to_bucket(ts: datetime, seconds: int) -> datetime:
    """Round *ts* down to the nearest bucket boundary."""
    epoch = datetime(1970, 1, 1, tzinfo=ts.tzinfo)
    delta = ts - epoch
    floored = (int(delta.total_seconds()) // seconds) * seconds
    return epoch + timedelta(seconds=floored)


def bucket_key(ts: datetime, seconds: int) -> _BucketKey:
    """Return an ISO-8601 string for the bucket that *ts* falls into."""
    return _floor_to_bucket(ts, seconds).strftime("%Y-%m-%dT%H:%M:%S")


def aggregate(
    lines: Iterable[str],
    line_parser: Callable[[str], datetime | None],
    bucket_seconds: int = 60,
) -> Dict[_BucketKey, int]:
    """Count log lines per time bucket.

    Lines whose timestamp cannot be parsed are silently skipped.

    Args:
        lines: Iterable of raw log line strings.
        line_parser: Callable that returns a ``datetime`` or ``None``.
        bucket_seconds: Width of each bucket in seconds (default: 60).

    Returns:
        Ordered dict mapping bucket key -> line count.
    """
    if bucket_seconds <= 0:
        raise ValueError("bucket_seconds must be a positive integer")

    counts: Dict[_BucketKey, int] = defaultdict(int)
    for line in lines:
        ts = line_parser(line)
        if ts is None:
            continue
        key = bucket_key(ts, bucket_seconds)
        counts[key] += 1

    return dict(sorted(counts.items()))


def iter_buckets(
    counts: Dict[_BucketKey, int],
) -> Iterator[Tuple[_BucketKey, int]]:
    """Yield *(bucket_key, count)* pairs in chronological order."""
    yield from sorted(counts.items())


def top_buckets(
    counts: Dict[_BucketKey, int], n: int = 5
) -> List[Tuple[_BucketKey, int]]:
    """Return the *n* busiest buckets, highest count first."""
    return sorted(counts.items(), key=lambda kv: kv[1], reverse=True)[:n]
