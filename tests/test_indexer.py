"""Tests for logslice.indexer."""
from __future__ import annotations

import pytest
from datetime import datetime, timezone

from logslice.indexer import LogIndex, build_index


def _dt(hour: int, minute: int = 0) -> datetime:
    return datetime(2024, 1, 1, hour, minute, tzinfo=timezone.utc)


def _line(hour: int, minute: int = 0, msg: str = "some log message") -> str:
    ts = _dt(hour, minute).strftime("%Y-%m-%dT%H:%M:%SZ")
    return f"{ts} INFO {msg}\n"


# ---------------------------------------------------------------------------
# LogIndex unit tests
# ---------------------------------------------------------------------------

class TestLogIndex:
    def test_nearest_offset_before_empty_returns_zero(self):
        idx = LogIndex()
        assert idx.nearest_offset_before(_dt(12)) == 0

    def test_nearest_offset_before_exact_match(self):
        idx = LogIndex()
        idx.add(_dt(10), 100)
        idx.add(_dt(12), 500)
        assert idx.nearest_offset_before(_dt(12)) == 500

    def test_nearest_offset_before_between_entries(self):
        idx = LogIndex()
        idx.add(_dt(10), 100)
        idx.add(_dt(14), 900)
        assert idx.nearest_offset_before(_dt(12)) == 100

    def test_nearest_offset_before_ts_earlier_than_all(self):
        idx = LogIndex()
        idx.add(_dt(10), 200)
        assert idx.nearest_offset_before(_dt(8)) == 0

    def test_nearest_offset_before_ts_after_all(self):
        idx = LogIndex()
        idx.add(_dt(10), 200)
        idx.add(_dt(12), 800)
        assert idx.nearest_offset_before(_dt(23)) == 800


# ---------------------------------------------------------------------------
# build_index tests
# ---------------------------------------------------------------------------

def test_build_index_every_1_indexes_all_parseable_lines():
    lines = [_line(h) for h in range(5)]
    idx = build_index(lines, every_n=1)
    assert len(idx.entries) == 5


def test_build_index_every_n_samples_correctly():
    lines = [_line(0, m) for m in range(10)]
    idx = build_index(lines, every_n=3)
    # Lines 0, 3, 6, 9 → 4 entries
    assert len(idx.entries) == 4


def test_build_index_zero_raises():
    with pytest.raises(ValueError):
        build_index([], every_n=0)


def test_build_index_negative_raises():
    with pytest.raises(ValueError):
        build_index([], every_n=-1)


def test_build_index_skips_unparseable_lines():
    lines = ["not a timestamp line\n", _line(10), _line(11)]
    idx = build_index(lines, every_n=1)
    # First line has no parseable timestamp, so only 2 entries
    assert len(idx.entries) == 2


def test_build_index_offsets_accumulate():
    line0 = _line(10)
    line1 = _line(11)
    idx = build_index([line0, line1], every_n=1)
    assert idx.entries[0][1] == 0
    assert idx.entries[1][1] == len(line0.encode("utf-8"))


def test_build_index_start_offset_applied():
    lines = [_line(10)]
    idx = build_index(lines, every_n=1, start_offset=256)
    assert idx.entries[0][1] == 256


def test_build_index_custom_parser():
    def always_none(_line):
        return None

    lines = [_line(10), _line(11)]
    idx = build_index(lines, every_n=1, line_parser=always_none)
    assert len(idx.entries) == 0


def test_nearest_offset_guides_search():
    lines = [_line(h) for h in range(24)]
    idx = build_index(lines, every_n=1)
    # Offset for hour 10 should be less than offset for hour 20
    off10 = idx.nearest_offset_before(_dt(10))
    off20 = idx.nearest_offset_before(_dt(20))
    assert off10 < off20
