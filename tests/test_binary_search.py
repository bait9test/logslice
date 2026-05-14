"""Tests for binary_search module."""

import io
from datetime import datetime, timezone
from unittest.mock import patch

import pytest

from logslice.binary_search import find_line_start, read_line_at, binary_search_offset


LOG_LINES = [
    b"2024-01-01T00:00:01Z INFO starting up\n",
    b"2024-01-01T00:00:02Z DEBUG connection opened\n",
    b"2024-01-01T00:00:03Z INFO request received\n",
    b"2024-01-01T00:00:04Z WARN slow query detected\n",
    b"2024-01-01T00:00:05Z ERROR timeout occurred\n",
]

LOG_CONTENT = b"".join(LOG_LINES)


def make_ts(second: int) -> datetime:
    return datetime(2024, 1, 1, 0, 0, second, tzinfo=timezone.utc)


def parse_line_ts(line: bytes):
    try:
        ts_str = line.split(b" ")[0].decode()
        return datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
    except Exception:
        return None


@pytest.fixture
def log_file():
    return io.BytesIO(LOG_CONTENT)


def test_find_line_start_at_zero(log_file):
    assert find_line_start(log_file, 0) == 0


def test_find_line_start_mid_line(log_file):
    # Position 5 is inside the first line; should return 0
    assert find_line_start(log_file, 5) == 0


def test_find_line_start_second_line(log_file):
    second_line_start = len(LOG_LINES[0])
    # Position at start of second line should return itself
    assert find_line_start(log_file, second_line_start) == second_line_start


def test_read_line_at_beginning(log_file):
    line = read_line_at(log_file, 0)
    assert line == LOG_LINES[0]


def test_read_line_at_mid_of_first_line(log_file):
    line = read_line_at(log_file, 10)
    assert line == LOG_LINES[0]


def test_read_line_at_second_line(log_file):
    pos = len(LOG_LINES[0])
    line = read_line_at(log_file, pos)
    assert line == LOG_LINES[1]


def test_binary_search_find_first(log_file):
    target = make_ts(3)
    offset = binary_search_offset(log_file, target, len(LOG_CONTENT), parse_line_ts, find_first=True)
    log_file.seek(offset)
    line = log_file.readline()
    assert b"00:00:03" in line


def test_binary_search_find_last(log_file):
    target = make_ts(3)
    offset = binary_search_offset(log_file, target, len(LOG_CONTENT), parse_line_ts, find_first=False)
    log_file.seek(offset)
    line = log_file.readline()
    assert b"00:00:03" in line


def test_binary_search_target_before_all(log_file):
    target = make_ts(0)
    offset = binary_search_offset(log_file, target, len(LOG_CONTENT), parse_line_ts, find_first=True)
    log_file.seek(offset)
    line = log_file.readline()
    assert b"00:00:01" in line


def test_binary_search_target_after_all(log_file):
    target = make_ts(99)
    offset = binary_search_offset(log_file, target, len(LOG_CONTENT), parse_line_ts, find_first=True)
    assert offset == len(LOG_CONTENT)
