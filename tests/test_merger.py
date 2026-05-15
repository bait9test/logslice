"""Tests for logslice.merger."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional

import pytest

from logslice.merger import merge_logs


def _key(line: str) -> Optional[float]:
    """Simple numeric key: first token must be parseable as a float."""
    try:
        return float(line.split()[0])
    except (ValueError, IndexError):
        return None


def _lines(*values: float) -> List[str]:
    return [f"{v:.1f} log entry\n" for v in values]


# ---------------------------------------------------------------------------
# basic merge
# ---------------------------------------------------------------------------

def test_merge_two_streams_sorted():
    a = _lines(1.0, 3.0, 5.0)
    b = _lines(2.0, 4.0, 6.0)
    result = list(merge_logs([a, b], key=_key))
    keys = [float(l.split()[0]) for l in result]
    assert keys == sorted(keys)
    assert len(result) == 6


def test_merge_single_stream_passthrough():
    a = _lines(1.0, 2.0, 3.0)
    result = list(merge_logs([a], key=_key))
    assert len(result) == 3


def test_merge_empty_streams():
    result = list(merge_logs([[], []], key=_key))
    assert result == []


def test_merge_one_empty_one_nonempty():
    a = _lines(1.0, 2.0)
    result = list(merge_logs([[], a], key=_key))
    assert len(result) == 2


def test_merge_three_streams():
    a = _lines(1.0, 4.0)
    b = _lines(2.0, 5.0)
    c = _lines(3.0, 6.0)
    result = list(merge_logs([a, b, c], key=_key))
    keys = [float(l.split()[0]) for l in result]
    assert keys == sorted(keys)
    assert len(result) == 6


# ---------------------------------------------------------------------------
# unparseable lines
# ---------------------------------------------------------------------------

def test_unparseable_placed_at_front_by_default():
    bad = ["no-timestamp line\n"]
    good = _lines(1.0, 2.0)
    result = list(merge_logs([bad, good], key=_key))
    assert result[0] == "no-timestamp line\n"


def test_drop_unparseable_removes_bad_lines():
    bad = ["no-timestamp line\n"]
    good = _lines(1.0, 2.0)
    result = list(merge_logs([bad, good], key=_key, drop_unparseable=True))
    assert all("no-timestamp" not in l for l in result)
    assert len(result) == 2


# ---------------------------------------------------------------------------
# tie-breaking (same timestamp)
# ---------------------------------------------------------------------------

def test_equal_timestamps_all_included():
    a = _lines(1.0, 1.0)
    b = _lines(1.0, 1.0)
    result = list(merge_logs([a, b], key=_key))
    assert len(result) == 4
