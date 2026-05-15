"""Tests for logslice.splitter."""

from datetime import datetime, timedelta, timezone
from typing import List, Optional

import pytest

from logslice.splitter import split_by_count, split_by_time


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _ts(minutes: int) -> datetime:
    return datetime(2024, 1, 1, 0, minutes, 0, tzinfo=timezone.utc)


def _line(minutes: int, msg: str = "msg") -> str:
    return f"2024-01-01T00:{minutes:02d}:00Z INFO {msg}\n"


def _key(line: str) -> Optional[datetime]:
    """Toy parser: extract minute from lines produced by _line()."""
    try:
        minute = int(line[14:16])
        return _ts(minute)
    except (ValueError, IndexError):
        return None


# ---------------------------------------------------------------------------
# split_by_count
# ---------------------------------------------------------------------------

def test_split_by_count_even_chunks():
    lines = [f"line {i}\n" for i in range(6)]
    result = list(split_by_count(lines, 2))
    assert result == [["line 0\n", "line 1\n"], ["line 2\n", "line 3\n"], ["line 4\n", "line 5\n"]]


def test_split_by_count_partial_last_chunk():
    lines = [f"line {i}\n" for i in range(5)]
    result = list(split_by_count(lines, 3))
    assert len(result) == 2
    assert len(result[-1]) == 2


def test_split_by_count_larger_than_input():
    lines = ["a\n", "b\n"]
    result = list(split_by_count(lines, 10))
    assert result == [["a\n", "b\n"]]


def test_split_by_count_empty_input():
    assert list(split_by_count([], 5)) == []


def test_split_by_count_zero_raises():
    with pytest.raises(ValueError):
        list(split_by_count(["x\n"], 0))


def test_split_by_count_negative_raises():
    with pytest.raises(ValueError):
        list(split_by_count(["x\n"], -3))


# ---------------------------------------------------------------------------
# split_by_time
# ---------------------------------------------------------------------------

def test_split_by_time_groups_within_window():
    lines = [_line(0), _line(1), _line(5), _line(6)]
    result = list(split_by_time(lines, timedelta(minutes=3), line_parser=_key))
    assert len(result) == 2
    assert result[0] == [_line(0), _line(1)]
    assert result[1] == [_line(5), _line(6)]


def test_split_by_time_single_chunk_when_all_within_window():
    lines = [_line(0), _line(1), _line(2)]
    result = list(split_by_time(lines, timedelta(minutes=10), line_parser=_key))
    assert result == [[_line(0), _line(1), _line(2)]]


def test_split_by_time_empty_input():
    assert list(split_by_time([], timedelta(minutes=5), line_parser=_key)) == []


def test_split_by_time_lines_without_timestamp_stay_in_current_chunk():
    lines = [_line(0), "no-timestamp\n", _line(1)]
    result = list(split_by_time(lines, timedelta(minutes=10), line_parser=_key))
    assert result == [[_line(0), "no-timestamp\n", _line(1)]]


def test_split_by_time_zero_interval_raises():
    with pytest.raises(ValueError):
        list(split_by_time([_line(0)], timedelta(seconds=0), line_parser=_key))


def test_split_by_time_negative_interval_raises():
    with pytest.raises(ValueError):
        list(split_by_time([_line(0)], timedelta(seconds=-1), line_parser=_key))
