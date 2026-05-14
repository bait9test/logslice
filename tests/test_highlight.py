"""Tests for logslice.highlight."""

from __future__ import annotations

import pytest

from logslice.highlight import (
    highlight_level,
    highlight_lines,
    highlight_term,
)

_RESET = "\033[0m"


def _strip_ansi(text: str) -> str:
    import re
    return re.sub(r"\033\[[0-9;]*m", "", text)


# ---------------------------------------------------------------------------
# highlight_term
# ---------------------------------------------------------------------------

def test_highlight_term_wraps_match():
    result = highlight_term("hello world", "world")
    assert "world" in _strip_ansi(result)
    assert _RESET in result  # colour code was injected


def test_highlight_term_case_insensitive():
    result = highlight_term("Hello World", "hello")
    assert _RESET in result


def test_highlight_term_empty_term_returns_unchanged():
    line = "nothing to highlight"
    assert highlight_term(line, "") == line


def test_highlight_term_unknown_colour_falls_back():
    # should not raise; unknown colour uses magenta fallback
    result = highlight_term("test line", "test", colour="nonexistent")
    assert "test" in _strip_ansi(result)


# ---------------------------------------------------------------------------
# highlight_level
# ---------------------------------------------------------------------------

def test_highlight_level_error():
    line = "2024-01-01 ERROR something broke"
    result = highlight_level(line)
    assert _RESET in result
    assert _strip_ansi(result) == line


def test_highlight_level_warning():
    line = "2024-01-01 WARNING disk almost full"
    result = highlight_level(line)
    assert _RESET in result


def test_highlight_level_no_match_unchanged():
    line = "2024-01-01 plain log line"
    assert highlight_level(line) == line


def test_highlight_level_preserves_newline():
    line = "2024-01-01 INFO starting up\n"
    result = highlight_level(line)
    assert result.endswith("\n")
    assert _strip_ansi(result) == line


# ---------------------------------------------------------------------------
# highlight_lines (pipeline)
# ---------------------------------------------------------------------------

def test_highlight_lines_by_level():
    lines = ["INFO ok\n", "ERROR bad\n", "plain\n"]
    results = list(highlight_lines(lines, by_level=True))
    assert len(results) == 3
    assert _RESET in results[0]  # INFO coloured
    assert _RESET in results[1]  # ERROR coloured
    assert results[2] == "plain\n"  # unchanged


def test_highlight_lines_term():
    lines = ["found needle here\n", "nothing here\n"]
    results = list(highlight_lines(lines, term="needle"))
    assert _RESET in results[0]
    assert results[1] == "nothing here\n"


def test_highlight_lines_both():
    lines = ["ERROR needle found\n"]
    results = list(highlight_lines(lines, term="needle", by_level=True))
    # both level colour and term colour applied
    assert results[0].count(_RESET) >= 2


def test_highlight_lines_no_options_passthrough():
    lines = ["line one\n", "line two\n"]
    results = list(highlight_lines(lines))
    assert results == lines
