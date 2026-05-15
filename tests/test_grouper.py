"""Tests for logslice.grouper."""
from __future__ import annotations

import pytest

from logslice.grouper import (
    group_by,
    group_counts,
    iter_groups,
    top_groups,
)


def _key(line: str) -> str:
    """Return the second token (simulating a log-level field)."""
    parts = line.split(None)
    return parts[1] if len(parts) > 1 else ""


LINES = [
    "2024-01-01 INFO  app started\n",
    "2024-01-01 DEBUG loading config\n",
    "2024-01-01 INFO  request received\n",
    "2024-01-01 ERROR something failed\n",
    "2024-01-01 INFO  request done\n",
    "2024-01-01 DEBUG cache miss\n",
]


def test_group_by_returns_all_keys():
    result = group_by(LINES, key_fn=_key)
    assert set(result.keys()) == {"INFO", "DEBUG", "ERROR"}


def test_group_by_correct_counts():
    result = group_by(LINES, key_fn=_key)
    assert len(result["INFO"]) == 3
    assert len(result["DEBUG"]) == 2
    assert len(result["ERROR"]) == 1


def test_group_by_empty_input():
    result = group_by([], key_fn=_key)
    assert result == {}


def test_iter_groups_preserves_insertion_order():
    keys = [k for k, _ in iter_groups(LINES, key_fn=_key)]
    assert keys == ["INFO", "DEBUG", "ERROR"]


def test_iter_groups_lines_match():
    groups = dict(iter_groups(LINES, key_fn=_key))
    assert groups["ERROR"] == ["2024-01-01 ERROR something failed\n"]


def test_group_counts_sums_correctly():
    counts = group_counts(LINES, key_fn=_key)
    assert counts == {"INFO": 3, "DEBUG": 2, "ERROR": 1}


def test_group_counts_empty():
    assert group_counts([]) == {}


def test_top_groups_returns_n():
    result = top_groups(LINES, n=2, key_fn=_key)
    assert len(result) == 2


def test_top_groups_sorted_descending():
    result = top_groups(LINES, n=3, key_fn=_key)
    counts = [c for _, c in result]
    assert counts == sorted(counts, reverse=True)


def test_top_groups_first_is_most_frequent():
    result = top_groups(LINES, n=1, key_fn=_key)
    assert result[0] == ("INFO", 3)


def test_top_groups_zero_raises():
    with pytest.raises(ValueError):
        top_groups(LINES, n=0, key_fn=_key)


def test_default_key_uses_first_token():
    """Without a custom key_fn the default splits on whitespace and takes [0]."""
    lines = ["alpha one\n", "beta two\n", "alpha three\n"]
    counts = group_counts(lines)
    assert counts == {"alpha": 2, "beta": 1}


def test_empty_line_grouped_under_empty_string():
    lines = ["\n", "foo bar\n", "\n"]
    counts = group_counts(lines)
    assert counts.get("", 0) == 2
