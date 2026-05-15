"""Tests for logslice.normalizer."""

from __future__ import annotations

import pytest

from logslice.normalizer import (
    normalize_level,
    normalize_line,
    normalize_lines,
    normalize_whitespace,
)


# ---------------------------------------------------------------------------
# normalize_whitespace
# ---------------------------------------------------------------------------

def test_normalize_whitespace_collapses_spaces():
    assert normalize_whitespace("foo   bar") == "foo bar"


def test_normalize_whitespace_collapses_tabs():
    assert normalize_whitespace("foo\t\tbar") == "foo bar"


def test_normalize_whitespace_preserves_trailing_newline():
    result = normalize_whitespace("foo   bar\n")
    assert result == "foo bar\n"


def test_normalize_whitespace_strips_leading_spaces():
    assert normalize_whitespace("  hello") == "hello"


def test_normalize_whitespace_empty_string():
    assert normalize_whitespace("") == ""


# ---------------------------------------------------------------------------
# normalize_level
# ---------------------------------------------------------------------------

def test_normalize_level_warn_to_WARNING():
    assert normalize_level("[warn] something happened") == "[WARNING] something happened"


def test_normalize_level_err_to_ERROR():
    assert normalize_level("err: disk full") == "ERROR: disk full"


def test_normalize_level_case_insensitive():
    assert normalize_level("WARN connection reset") == "WARNING connection reset"


def test_normalize_level_info_unchanged_canonical():
    # "INFO" is already canonical but the regex still matches "info" token
    result = normalize_level("info: started")
    assert result == "INFO: started"


def test_normalize_level_no_level_token():
    line = "2024-01-01 some message without level"
    assert normalize_level(line) == line


# ---------------------------------------------------------------------------
# normalize_line
# ---------------------------------------------------------------------------

def test_normalize_line_applies_both():
    result = normalize_line("  warn   disk  full  \n")
    assert result == "WARNING disk full\n"


def test_normalize_line_fix_level_false():
    result = normalize_line("  warn  msg", fix_level=False)
    assert result == "warn msg"


def test_normalize_line_fix_whitespace_false():
    result = normalize_line("warn   msg", fix_whitespace=False)
    assert result == "WARNING   msg"


# ---------------------------------------------------------------------------
# normalize_lines
# ---------------------------------------------------------------------------

def test_normalize_lines_yields_all():
    lines = ["warn  a\n", "err  b\n"]
    result = list(normalize_lines(lines))
    assert result == ["WARNING a\n", "ERROR b\n"]


def test_normalize_lines_custom_transform():
    lines = ["info hello\n"]
    result = list(normalize_lines(lines, transform=str.upper))
    assert result == ["INFO HELLO\n"]


def test_normalize_lines_empty_input():
    assert list(normalize_lines([])) == []
