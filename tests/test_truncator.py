"""Tests for logslice.truncator."""

import pytest

from logslice.truncator import _ELLIPSIS, truncate_line, truncate_lines


# ---------------------------------------------------------------------------
# truncate_line
# ---------------------------------------------------------------------------

def test_short_line_unchanged():
    line = "2024-01-01 INFO hello\n"
    assert truncate_line(line, max_len=120) == line


def test_exact_length_unchanged():
    body = "x" * 40
    assert truncate_line(body, max_len=40) == body


def test_long_line_contains_ellipsis():
    body = "A" * 60 + "B" * 60
    result = truncate_line(body, max_len=80)
    assert _ELLIPSIS in result


def test_long_line_respects_max_len():
    body = "A" * 200
    max_len = 80
    result = truncate_line(body, max_len=max_len)
    assert len(result) == max_len


def test_head_and_tail_preserved():
    head = "START"
    tail = "FINISH"
    body = head + "x" * 200 + tail
    result = truncate_line(body, max_len=30)
    assert result.startswith(head)
    assert result.endswith(tail)


def test_trailing_newline_preserved_when_long():
    body = "Z" * 200
    result = truncate_line(body + "\n", max_len=80)
    assert result.endswith("\n")
    # The non-newline portion should equal max_len
    assert len(result.rstrip("\n")) == 80


def test_trailing_newline_preserved_when_short():
    line = "short line\n"
    assert truncate_line(line, max_len=120) == line


def test_no_trailing_newline_not_added():
    body = "A" * 200
    result = truncate_line(body, max_len=80)
    assert not result.endswith("\n")


def test_invalid_max_len_raises():
    with pytest.raises(ValueError):
        truncate_line("hello world", max_len=5)


# ---------------------------------------------------------------------------
# truncate_lines
# ---------------------------------------------------------------------------

def test_truncate_lines_yields_all():
    lines = ["short\n", "A" * 200 + "\n", "also short\n"]
    result = list(truncate_lines(lines, max_len=80))
    assert len(result) == 3


def test_truncate_lines_long_lines_shortened():
    lines = ["X" * 300 + "\n"] * 5
    for r in truncate_lines(lines, max_len=80):
        assert len(r.rstrip("\n")) == 80


def test_truncate_lines_empty_input():
    assert list(truncate_lines([], max_len=80)) == []


def test_truncate_lines_default_max():
    lines = ["Y" * 200]
    (result,) = truncate_lines(lines)
    assert len(result) == 120
