"""Tests for logslice.differ."""
from __future__ import annotations

import pytest

from logslice.differ import diff_logs, diff_summary


LEFT = ["alpha\n", "beta\n", "gamma\n"]
RIGHT = ["beta\n", "gamma\n", "delta\n"]


def _tags(results):
    return [tag for tag, _ in results]


def _lines(results):
    return [line.rstrip("\n") for _, line in results]


# --- diff_logs ---

def test_mode_all_contains_all_tags():
    tags = _tags(list(diff_logs(LEFT, RIGHT, mode="all")))
    assert "<" in tags
    assert ">" in tags
    assert "=" in tags


def test_mode_left_only_left_unique():
    results = list(diff_logs(LEFT, RIGHT, mode="left"))
    assert all(t == "<" for t, _ in results)
    assert "alpha" in _lines(results)
    assert "beta" not in _lines(results)


def test_mode_right_only_right_unique():
    results = list(diff_logs(LEFT, RIGHT, mode="right"))
    assert all(t == ">" for t, _ in results)
    assert "delta" in _lines(results)


def test_mode_common_only_shared():
    results = list(diff_logs(LEFT, RIGHT, mode="common"))
    assert all(t == "=" for t, _ in results)
    lines = _lines(results)
    assert "beta" in lines
    assert "gamma" in lines
    assert "alpha" not in lines


def test_identical_streams_all_common():
    results = list(diff_logs(LEFT, LEFT, mode="all"))
    tags = _tags(results)
    assert "<" not in tags
    assert ">" not in tags
    assert "=" in tags


def test_disjoint_streams_no_common():
    a = ["x\n", "y\n"]
    b = ["p\n", "q\n"]
    results = list(diff_logs(a, b, mode="common"))
    assert results == []


def test_empty_left():
    results = list(diff_logs([], RIGHT, mode="all"))
    tags = _tags(results)
    assert "<" not in tags
    assert ">" in tags


def test_empty_right():
    results = list(diff_logs(LEFT, [], mode="all"))
    tags = _tags(results)
    assert ">" not in tags
    assert "<" in tags


def test_both_empty():
    assert list(diff_logs([], [], mode="all")) == []


def test_lines_end_with_newline():
    results = list(diff_logs(LEFT, RIGHT, mode="all"))
    for _, line in results:
        assert line.endswith("\n")


# --- diff_summary ---

def test_summary_counts():
    s = diff_summary(LEFT, RIGHT)
    assert s["left_only"] == 1    # alpha
    assert s["right_only"] == 1   # delta
    assert s["common"] == 2       # beta, gamma


def test_summary_identical():
    s = diff_summary(LEFT, LEFT)
    assert s["left_only"] == 0
    assert s["right_only"] == 0
    assert s["common"] == len(LEFT)


def test_summary_empty():
    s = diff_summary([], [])
    assert s == {"left_only": 0, "right_only": 0, "common": 0}
