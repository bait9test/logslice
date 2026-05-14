"""Tests for logslice.timestamp_parser."""

import pytest
from datetime import datetime
from logslice.timestamp_parser import parse_timestamp, parse_user_timestamp


class TestParseTimestamp:
    def test_iso8601_with_microseconds(self):
        line = "2024-03-10T08:22:11.456789 INFO server started"
        dt = parse_timestamp(line)
        assert dt == datetime(2024, 3, 10, 8, 22, 11, 456789)

    def test_iso8601_no_microseconds(self):
        line = "2024-03-10T08:22:11 ERROR something failed"
        dt = parse_timestamp(line)
        assert dt == datetime(2024, 3, 10, 8, 22, 11)

    def test_space_separated_with_milliseconds(self):
        line = "2024-03-10 08:22:11,123 DEBUG connecting"
        dt = parse_timestamp(line)
        assert dt == datetime(2024, 3, 10, 8, 22, 11, 123000)

    def test_space_separated_no_millis(self):
        line = "2024-03-10 08:22:11 WARN disk usage high"
        dt = parse_timestamp(line)
        assert dt == datetime(2024, 3, 10, 8, 22, 11)

    def test_apache_format(self):
        line = '127.0.0.1 - - [10/Mar/2024:08:22:11 +0000] "GET / HTTP/1.1" 200'
        dt = parse_timestamp(line)
        assert dt == datetime(2024, 3, 10, 8, 22, 11)

    def test_syslog_format(self):
        line = "Mar 10 08:22:11 myhost sshd[1234]: Accepted"
        dt = parse_timestamp(line)
        assert dt is not None
        assert dt.month == 3
        assert dt.day == 10
        assert dt.hour == 8
        assert dt.year == datetime.now().year

    def test_no_timestamp_returns_none(self):
        line = "this line has no timestamp at all"
        assert parse_timestamp(line) is None

    def test_empty_line_returns_none(self):
        assert parse_timestamp("") is None


class TestParseUserTimestamp:
    @pytest.mark.parametrize("value,expected", [
        ("2024-03-10T08:22:11", datetime(2024, 3, 10, 8, 22, 11)),
        ("2024-03-10 08:22:11", datetime(2024, 3, 10, 8, 22, 11)),
        ("2024-03-10T08:22", datetime(2024, 3, 10, 8, 22)),
        ("2024-03-10 08:22", datetime(2024, 3, 10, 8, 22)),
        ("2024-03-10", datetime(2024, 3, 10)),
    ])
    def test_valid_formats(self, value, expected):
        assert parse_user_timestamp(value) == expected

    def test_invalid_format_raises(self):
        with pytest.raises(ValueError, match="Cannot parse timestamp"):
            parse_user_timestamp("not-a-date")

    def test_partial_date_raises(self):
        with pytest.raises(ValueError):
            parse_user_timestamp("2024/03/10")
