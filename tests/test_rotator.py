"""Tests for logslice.rotator."""

from __future__ import annotations

import io
from pathlib import Path

import pytest

from logslice.rotator import (
    _rotated_siblings,
    count_rotated_segments,
    iter_rotated_lines,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_log_tree(tmp_path: Path) -> Path:
    """Create a small rotation tree and return the live log path."""
    live = tmp_path / "app.log"
    live.write_text("live line 1\nlive line 2\n")
    (tmp_path / "app.log.1").write_text("recent line 1\nrecent line 2\n")
    (tmp_path / "app.log.2").write_text("old line 1\n")
    # A .gz variant should also be discovered (index 3)
    (tmp_path / "app.log.3.gz").write_text("ignored gz content\n")
    return live


# ---------------------------------------------------------------------------
# _rotated_siblings
# ---------------------------------------------------------------------------

def test_rotated_siblings_sorted_oldest_first(tmp_path):
    live = _make_log_tree(tmp_path)
    siblings = _rotated_siblings(live)
    names = [p.name for p in siblings]
    # highest numeric index first (oldest)
    assert names[0] in ("app.log.3.gz", "app.log.2")
    assert names[-1] == "app.log.1"


def test_rotated_siblings_empty_when_none(tmp_path):
    live = tmp_path / "app.log"
    live.write_text("only file\n")
    assert _rotated_siblings(live) == []


def test_rotated_siblings_ignores_unrelated_files(tmp_path):
    live = tmp_path / "app.log"
    live.write_text("x\n")
    (tmp_path / "other.log.1").write_text("unrelated\n")
    assert _rotated_siblings(live) == []


# ---------------------------------------------------------------------------
# count_rotated_segments
# ---------------------------------------------------------------------------

def test_count_rotated_segments(tmp_path):
    live = _make_log_tree(tmp_path)
    assert count_rotated_segments(live) == 3  # .1, .2, .3.gz


def test_count_rotated_segments_zero(tmp_path):
    live = tmp_path / "app.log"
    live.write_text("only\n")
    assert count_rotated_segments(live) == 0


# ---------------------------------------------------------------------------
# iter_rotated_lines
# ---------------------------------------------------------------------------

def test_iter_rotated_lines_order(tmp_path):
    live = _make_log_tree(tmp_path)
    # Skip .gz file by only creating plain siblings for this test
    (tmp_path / "app.log.3.gz").unlink()
    lines = list(iter_rotated_lines(live))
    # old line from .2 must appear before recent from .1 and live
    old_idx = next(i for i, l in enumerate(lines) if "old line" in l)
    recent_idx = next(i for i, l in enumerate(lines) if "recent line" in l)
    live_idx = next(i for i, l in enumerate(lines) if "live line" in l)
    assert old_idx < recent_idx < live_idx


def test_iter_rotated_lines_skip_rotated(tmp_path):
    live = _make_log_tree(tmp_path)
    (tmp_path / "app.log.3.gz").unlink()
    lines = list(iter_rotated_lines(live, include_rotated=False))
    assert all("live" in l for l in lines)
    assert len(lines) == 2


def test_iter_rotated_lines_missing_segment_skipped(tmp_path):
    live = tmp_path / "app.log"
    live.write_text("live\n")
    # Segment .1 does not exist — should not raise
    lines = list(iter_rotated_lines(live))
    assert lines == ["live\n"]
