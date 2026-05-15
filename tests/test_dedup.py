"""Tests for logslice.dedup."""

from __future__ import annotations

import pytest

from logslice.dedup import _line_key, dedup_exact, dedup_window


# ---------------------------------------------------------------------------
# _line_key
# ---------------------------------------------------------------------------

def test_line_key_strips_timestamp():
    a = "2024-01-01T00:00:00 ERROR something went wrong"
    b = "2024-06-15T12:34:56 ERROR something went wrong"
    assert _line_key(a) == _line_key(b)


def test_line_key_different_messages():
    a = "2024-01-01T00:00:00 ERROR foo"
    b = "2024-01-01T00:00:00 ERROR bar"
    assert _line_key(a) != _line_key(b)


def test_line_key_single_token():
    # Should not raise even for a bare single-word line.
    key = _line_key("hello")
    assert isinstance(key, str) and len(key) == 32


# ---------------------------------------------------------------------------
# dedup_exact
# ---------------------------------------------------------------------------

def test_dedup_exact_removes_duplicates():
    lines = [
        "2024-01-01T00:00:01 INFO started",
        "2024-01-01T00:00:02 INFO started",
        "2024-01-01T00:00:03 INFO stopped",
    ]
    result = list(dedup_exact(lines))
    assert len(result) == 2
    assert result[0] == lines[0]
    assert result[1] == lines[2]


def test_dedup_exact_all_unique():
    lines = [
        "2024-01-01T00:00:01 INFO a",
        "2024-01-01T00:00:02 INFO b",
        "2024-01-01T00:00:03 INFO c",
    ]
    assert list(dedup_exact(lines)) == lines


def test_dedup_exact_empty():
    assert list(dedup_exact([])) == []


def test_dedup_exact_custom_key_fn():
    # Use the full line as key — timestamps differ so nothing deduped.
    lines = [
        "2024-01-01T00:00:01 INFO started",
        "2024-01-01T00:00:02 INFO started",
    ]
    result = list(dedup_exact(lines, key_fn=lambda l: l))
    assert result == lines


# ---------------------------------------------------------------------------
# dedup_window
# ---------------------------------------------------------------------------

def test_dedup_window_basic():
    lines = [
        "2024-01-01T00:00:01 INFO ping",
        "2024-01-01T00:00:02 INFO ping",
        "2024-01-01T00:00:03 INFO pong",
    ]
    result = list(dedup_window(lines, window=10))
    assert len(result) == 2


def test_dedup_window_reappears_after_eviction():
    # window=1 means only the immediately previous line is remembered.
    lines = [
        "2024-01-01T00:00:01 INFO ping",
        "2024-01-01T00:00:02 INFO pong",  # evicts 'ping' from window
        "2024-01-01T00:00:03 INFO ping",  # 'ping' no longer in window -> yielded
    ]
    result = list(dedup_window(lines, window=1))
    assert len(result) == 3


def test_dedup_window_zero_raises():
    with pytest.raises(ValueError, match="window must be >= 1"):
        list(dedup_window([], window=0))


def test_dedup_window_empty():
    assert list(dedup_window([], window=5)) == []
