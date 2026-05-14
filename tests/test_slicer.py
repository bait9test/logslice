"""Tests for logslice.slicer."""

import os
import tempfile
from datetime import datetime

import pytest

from logslice.slicer import default_line_parser, slice_log


LOG_LINES = [
    "2024-01-01T10:00:00 INFO  startup complete",
    "2024-01-01T10:01:00 DEBUG checking config",
    "2024-01-01T10:02:00 INFO  request received",
    "2024-01-01T10:03:00 WARN  slow response",
    "2024-01-01T10:04:00 ERROR timeout",
    "2024-01-01T10:05:00 INFO  shutdown",
]


@pytest.fixture()
def log_file(tmp_path):
    path = tmp_path / "app.log"
    path.write_text("\n".join(LOG_LINES) + "\n", encoding="utf-8")
    return str(path)


def ts(s: str) -> datetime:
    return datetime.fromisoformat(s)


def test_default_line_parser_iso():
    line = "2024-01-01T10:00:00 INFO startup"
    result = default_line_parser(line)
    assert result == datetime(2024, 1, 1, 10, 0, 0)


def test_default_line_parser_space_sep():
    line = "2024-01-01 10:00:00 INFO startup"
    result = default_line_parser(line)
    assert result == datetime(2024, 1, 1, 10, 0, 0)


def test_default_line_parser_empty():
    assert default_line_parser("") is None


def test_slice_full_range(log_file):
    lines = list(slice_log(log_file, ts("2024-01-01T10:00:00"), ts("2024-01-01T10:05:00")))
    assert len(lines) == 6


def test_slice_middle(log_file):
    lines = list(slice_log(log_file, ts("2024-01-01T10:02:00"), ts("2024-01-01T10:03:00")))
    assert len(lines) == 2
    assert "request received" in lines[0]
    assert "slow response" in lines[1]


def test_slice_single_line(log_file):
    lines = list(slice_log(log_file, ts("2024-01-01T10:04:00"), ts("2024-01-01T10:04:00")))
    assert len(lines) == 1
    assert "timeout" in lines[0]


def test_slice_before_range(log_file):
    lines = list(slice_log(log_file, ts("2024-01-01T09:00:00"), ts("2024-01-01T09:59:00")))
    assert lines == []


def test_slice_after_range(log_file):
    lines = list(slice_log(log_file, ts("2024-01-01T11:00:00"), ts("2024-01-01T12:00:00")))
    assert lines == []


def test_slice_empty_file(tmp_path):
    path = tmp_path / "empty.log"
    path.write_text("", encoding="utf-8")
    lines = list(slice_log(str(path), ts("2024-01-01T10:00:00"), ts("2024-01-01T11:00:00")))
    assert lines == []
