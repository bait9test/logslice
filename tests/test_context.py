"""Tests for logslice.context — context lines around slice results."""

import pytest
from logslice.context import with_context, context_window


LINES = [f"line{i}\n" for i in range(10)]


# ---------------------------------------------------------------------------
# with_context
# ---------------------------------------------------------------------------

def test_with_context_no_padding():
    result = list(with_context(LINES))
    assert result == LINES


def test_with_context_before_only():
    # All lines emitted; with before=2 the first 2 lines appear as context
    result = list(with_context(LINES[:5], before=2))
    assert result == LINES[:5]


def test_with_context_after_only():
    result = list(with_context(LINES[:5], after=2))
    assert result == LINES[:5]


def test_with_context_no_duplicates():
    """Even with large before/after windows, each line appears exactly once."""
    result = list(with_context(LINES, before=3, after=3))
    assert result == LINES
    assert len(result) == len(LINES)


def test_with_context_negative_raises():
    with pytest.raises(ValueError):
        list(with_context(LINES, before=-1))
    with pytest.raises(ValueError):
        list(with_context(LINES, after=-1))


# ---------------------------------------------------------------------------
# context_window
# ---------------------------------------------------------------------------

def test_context_window_no_matches():
    result = list(context_window(LINES, lambda l: "zzz" in l, before=2, after=2))
    assert result == []


def test_context_window_exact_match_only():
    result = list(context_window(LINES, lambda l: "line5" in l, before=0, after=0))
    assert result == ["line5\n"]


def test_context_window_before():
    result = list(context_window(LINES, lambda l: "line5" in l, before=2, after=0))
    assert result == ["line3\n", "line4\n", "line5\n"]


def test_context_window_after():
    result = list(context_window(LINES, lambda l: "line5" in l, before=0, after=2))
    assert result == ["line5\n", "line6\n", "line7\n"]


def test_context_window_before_and_after():
    result = list(context_window(LINES, lambda l: "line5" in l, before=1, after=1))
    assert result == ["line4\n", "line5\n", "line6\n"]


def test_context_window_overlapping_windows_no_duplicates():
    # line3 and line5 both match; with before=2 after=2 their windows overlap
    predicate = lambda l: "line3" in l or "line5" in l
    result = list(context_window(LINES, predicate, before=2, after=2))
    # Expected: line1..line7, each once
    expected = LINES[1:8]
    assert result == expected
    assert len(result) == len(set(result))


def test_context_window_boundary_clamp():
    """before/after should not go out of bounds."""
    result = list(context_window(LINES, lambda l: "line0" in l, before=5, after=0))
    assert result == ["line0\n"]

    result = list(context_window(LINES, lambda l: "line9" in l, before=0, after=5))
    assert result == ["line9\n"]


def test_context_window_negative_raises():
    with pytest.raises(ValueError):
        list(context_window(LINES, lambda l: True, before=-1))
