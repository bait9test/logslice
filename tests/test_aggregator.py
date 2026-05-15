"""Tests for logslice.aggregator."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from logslice.aggregator import aggregate, bucket_key, iter_buckets, top_buckets


def _dt(hour: int, minute: int, second: int = 0) -> datetime:
    return datetime(2024, 1, 15, hour, minute, second, tzinfo=timezone.utc)


def _make_line(ts: datetime, msg: str = "hello") -> str:
    return f"{ts.strftime('%Y-%m-%dT%H:%M:%S')} INFO {msg}\n"


def _parser(line: str) -> datetime | None:
    try:
        raw = line.split()[0]
        return datetime.strptime(raw, "%Y-%m-%dT%H:%M:%S").replace(
            tzinfo=timezone.utc
        )
    except (ValueError, IndexError):
        return None


# --- bucket_key ---

def test_bucket_key_floors_to_minute():
    ts = _dt(10, 5, 37)
    assert bucket_key(ts, 60) == "2024-01-15T10:05:00"


def test_bucket_key_floors_to_five_minutes():
    ts = _dt(10, 7, 0)
    assert bucket_key(ts, 300) == "2024-01-15T10:05:00"


def test_bucket_key_exact_boundary_unchanged():
    ts = _dt(10, 0, 0)
    assert bucket_key(ts, 60) == "2024-01-15T10:00:00"


# --- aggregate ---

def test_aggregate_counts_lines_per_bucket():
    lines = [
        _make_line(_dt(10, 0, 5)),
        _make_line(_dt(10, 0, 45)),
        _make_line(_dt(10, 1, 10)),
    ]
    result = aggregate(lines, _parser, bucket_seconds=60)
    assert result["2024-01-15T10:00:00"] == 2
    assert result["2024-01-15T10:01:00"] == 1


def test_aggregate_skips_unparseable_lines():
    lines = ["not a timestamp line\n", _make_line(_dt(9, 0, 0))]
    result = aggregate(lines, _parser, bucket_seconds=60)
    assert len(result) == 1


def test_aggregate_empty_input_returns_empty_dict():
    assert aggregate([], _parser) == {}


def test_aggregate_raises_on_zero_bucket():
    with pytest.raises(ValueError):
        aggregate([], _parser, bucket_seconds=0)


def test_aggregate_raises_on_negative_bucket():
    with pytest.raises(ValueError):
        aggregate([], _parser, bucket_seconds=-10)


def test_aggregate_result_is_sorted():
    lines = [
        _make_line(_dt(10, 2, 0)),
        _make_line(_dt(10, 0, 0)),
        _make_line(_dt(10, 1, 0)),
    ]
    keys = list(aggregate(lines, _parser, bucket_seconds=60).keys())
    assert keys == sorted(keys)


# --- iter_buckets ---

def test_iter_buckets_yields_sorted_pairs():
    counts = {"2024-01-15T10:02:00": 3, "2024-01-15T10:00:00": 1}
    pairs = list(iter_buckets(counts))
    assert pairs[0] == ("2024-01-15T10:00:00", 1)
    assert pairs[1] == ("2024-01-15T10:02:00", 3)


# --- top_buckets ---

def test_top_buckets_returns_highest_first():
    counts = {"a": 1, "b": 10, "c": 5}
    top = top_buckets(counts, n=2)
    assert top[0] == ("b", 10)
    assert top[1] == ("c", 5)


def test_top_buckets_n_larger_than_input():
    counts = {"a": 2, "b": 4}
    assert len(top_buckets(counts, n=100)) == 2
