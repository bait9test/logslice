"""Integration tests: normalizer pipeline with filters and formatter."""

from __future__ import annotations

from logslice.normalizer import normalize_lines
from logslice.filters import grep, filter_level, pipeline
from logslice.formatter import format_raw


RAW_LINES = [
    "2024-03-01T10:00:00 warn   disk usage high\n",
    "2024-03-01T10:01:00 info   all systems nominal\n",
    "2024-03-01T10:02:00 err    connection refused\n",
    "2024-03-01T10:03:00 debug  retry attempt 1\n",
    "2024-03-01T10:04:00 CRITICAL  process died\n",
]


def test_normalize_then_grep():
    normalized = list(normalize_lines(RAW_LINES))
    matched = list(grep(normalized, "WARNING"))
    assert len(matched) == 1
    assert "WARNING" in matched[0]


def test_normalize_then_filter_level():
    normalized = list(normalize_lines(RAW_LINES))
    errors = list(filter_level(normalized, min_level="ERROR"))
    levels_found = {line.split()[1] for line in errors}
    # Should contain ERROR and CRITICAL but not WARNING/INFO/DEBUG
    assert "ERROR" in levels_found
    assert "CRITICAL" in levels_found
    assert "WARNING" not in levels_found


def test_normalize_pipeline_with_grep_and_level():
    steps = [
        lambda lines: normalize_lines(lines),
        lambda lines: filter_level(lines, min_level="WARNING"),
    ]
    result = list(pipeline(RAW_LINES, steps))
    # warn->WARNING, err->ERROR, CRITICAL stay; info and debug dropped
    assert len(result) == 3


def test_normalize_whitespace_does_not_break_format_raw():
    lines = ["info   hello   world\n"]
    normalized = list(normalize_lines(lines))
    output = format_raw(normalized)
    assert "hello world" in output
    assert "  " not in output


def test_full_pipeline_output_is_clean():
    steps = [
        lambda lines: normalize_lines(lines),
        lambda lines: grep(lines, "disk"),
    ]
    result = list(pipeline(RAW_LINES, steps))
    assert len(result) == 1
    assert "WARNING" in result[0]
    assert "warn" not in result[0].split()[1]  # token itself is canonical
