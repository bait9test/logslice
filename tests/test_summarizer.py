"""Tests for logslice.summarizer."""

from collections import Counter

import pytest

from logslice.summarizer import (
    LogSummary,
    _extract_level,
    _extract_timestamp,
    format_summary,
    summarize_lines,
)


LINES = [
    "2024-01-10T08:00:00 INFO  service started successfully\n",
    "2024-01-10T08:00:01 DEBUG loading config from disk\n",
    "2024-01-10T08:00:02 ERROR failed to connect to database\n",
    "2024-01-10T08:00:03 WARN  retry attempt number one\n",
    "2024-01-10T08:00:04 ERROR timeout reached for database\n",
]


def test_total_lines():
    s = summarize_lines(LINES)
    assert s.total_lines == 5


def test_level_counts():
    s = summarize_lines(LINES)
    assert s.level_counts["INFO"] == 1
    assert s.level_counts["DEBUG"] == 1
    assert s.level_counts["ERROR"] == 2
    assert s.level_counts["WARN"] == 1


def test_first_and_last_timestamp():
    s = summarize_lines(LINES)
    assert s.first_timestamp == "2024-01-10T08:00:00"
    assert s.last_timestamp == "2024-01-10T08:00:04"


def test_top_terms_respects_top_n():
    s = summarize_lines(LINES, top_n=3)
    assert len(s.top_terms) <= 3


def test_top_terms_database_appears():
    s = summarize_lines(LINES, top_n=10)
    terms = [t for t, _ in s.top_terms]
    assert "database" in terms


def test_empty_input():
    s = summarize_lines([])
    assert s.total_lines == 0
    assert s.first_timestamp is None
    assert s.last_timestamp is None
    assert len(s.level_counts) == 0
    assert s.top_terms == []


def test_warning_normalised_to_warn():
    lines = ["2024-01-10T09:00:00 WARNING something odd happened\n"]
    s = summarize_lines(lines)
    assert s.level_counts["WARN"] == 1
    assert "WARNING" not in s.level_counts


def test_line_without_timestamp_still_counted():
    lines = ["INFO  no timestamp here\n"]
    s = summarize_lines(lines)
    assert s.total_lines == 1
    assert s.first_timestamp is None


def test_extract_level_returns_none_for_plain_line():
    assert _extract_level("nothing special here") is None


def test_extract_timestamp_space_separated():
    ts = _extract_timestamp("2024-03-15 12:34:56 INFO hello")
    assert ts == "2024-03-15 12:34:56"


def test_format_summary_contains_line_count():
    s = summarize_lines(LINES)
    out = format_summary(s)
    assert "5" in out


def test_format_summary_shows_levels():
    s = summarize_lines(LINES)
    out = format_summary(s)
    assert "ERROR=2" in out


def test_format_summary_empty():
    s = summarize_lines([])
    out = format_summary(s)
    assert "n/a" in out
