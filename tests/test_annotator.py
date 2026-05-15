"""Tests for logslice.annotator."""
from __future__ import annotations

import pytest

from logslice.annotator import annotate_offset, annotate_sequence, annotate_tag


LINES = ["alpha\n", "bravo\n", "charlie\n"]


# ---------------------------------------------------------------------------
# annotate_sequence
# ---------------------------------------------------------------------------

def test_sequence_default_start():
    result = list(annotate_sequence(LINES))
    assert result[0].startswith("1 ")
    assert result[1].startswith("2 ")
    assert result[2].startswith("3 ")


def test_sequence_custom_start():
    result = list(annotate_sequence(LINES, start=10))
    assert result[0].startswith("10 ")
    assert result[2].startswith("12 ")


def test_sequence_preserves_body():
    result = list(annotate_sequence(["hello\n"]))
    assert result[0].rstrip("\n").endswith("hello")


def test_sequence_adds_newline_if_missing():
    result = list(annotate_sequence(["no-newline"]))
    assert result[0].endswith("\n")


def test_sequence_prefix_suffix():
    result = list(annotate_sequence(["x\n"], prefix="[", suffix="] "))
    assert result[0].startswith("[1] ")


def test_sequence_negative_start_raises():
    with pytest.raises(ValueError, match="start"):
        list(annotate_sequence(LINES, start=-1))


def test_sequence_empty_input():
    assert list(annotate_sequence([])) == []


# ---------------------------------------------------------------------------
# annotate_tag
# ---------------------------------------------------------------------------

def test_tag_prepends_result_of_fn():
    result = list(annotate_tag(["foo\n", "bar\n"], tag_fn=lambda _: "TAG"))
    assert result[0].startswith("TAG ")
    assert result[1].startswith("TAG ")


def test_tag_fn_receives_original_line():
    received: list[str] = []

    def capture(line: str) -> str:
        received.append(line)
        return "X"

    list(annotate_tag(["hello\n"], tag_fn=capture))
    assert received == ["hello\n"]


def test_tag_body_preserved():
    result = list(annotate_tag(["world\n"], tag_fn=lambda _: ">>>"))
    assert "world" in result[0]


def test_tag_ends_with_newline():
    result = list(annotate_tag(["line"], tag_fn=lambda _: "T"))
    assert result[0].endswith("\n")


# ---------------------------------------------------------------------------
# annotate_offset
# ---------------------------------------------------------------------------

def test_offset_first_is_zero():
    pairs = list(annotate_offset(["abc\n"]))
    assert pairs[0][0] == 0


def test_offset_advances_by_byte_length():
    pairs = list(annotate_offset(["ab\n", "cde\n"]))
    assert pairs[0][0] == 0
    assert pairs[1][0] == len("ab\n".encode())


def test_offset_custom_start():
    pairs = list(annotate_offset(["x\n"], byte_start=100))
    assert pairs[0][0] == 100


def test_offset_negative_start_raises():
    with pytest.raises(ValueError, match="byte_start"):
        list(annotate_offset(["x\n"], byte_start=-5))


def test_offset_unicode_bytes():
    # '€' is 3 bytes in UTF-8
    line = "€\n"
    pairs = list(annotate_offset([line, "a\n"]))
    assert pairs[1][0] == len(line.encode("utf-8"))


def test_offset_empty_input():
    assert list(annotate_offset([])) == []
