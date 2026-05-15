"""Tests for logslice.transformer."""

from __future__ import annotations

import pytest

from logslice.transformer import (
    append_text,
    chain,
    prepend_text,
    replace_field,
    strip_ansi,
    transform_lines,
    uppercase_level,
)


# ---------------------------------------------------------------------------
# uppercase_level
# ---------------------------------------------------------------------------

def test_uppercase_level_info():
    assert uppercase_level("2024-01-01 info  service started\n") == "2024-01-01 INFO  service started\n"


def test_uppercase_level_warn_variants():
    assert uppercase_level("warn: disk low") == "WARN: disk low"
    assert uppercase_level("warning: disk low") == "WARNING: disk low"


def test_uppercase_level_leaves_unknown_words():
    line = "2024-01-01 verbose something\n"
    assert uppercase_level(line) == line


# ---------------------------------------------------------------------------
# strip_ansi
# ---------------------------------------------------------------------------

def test_strip_ansi_removes_colour_codes():
    coloured = "\x1b[32mINFO\x1b[0m message\n"
    assert strip_ansi(coloured) == "INFO message\n"


def test_strip_ansi_passthrough_plain():
    line = "plain line\n"
    assert strip_ansi(line) == line


# ---------------------------------------------------------------------------
# replace_field
# ---------------------------------------------------------------------------

def test_replace_field_substitutes_pattern():
    t = replace_field(r'\d{4}-\d{2}-\d{2}', 'DATE')
    assert t("2024-06-01 INFO boot\n") == "DATE INFO boot\n"


def test_replace_field_case_insensitive_flag():
    import re
    t = replace_field('error', 'ERR', flags=re.IGNORECASE)
    assert t("Error occurred\n") == "ERR occurred\n"


# ---------------------------------------------------------------------------
# prepend_text / append_text
# ---------------------------------------------------------------------------

def test_prepend_text_adds_prefix():
    t = prepend_text('[APP] ')
    assert t("INFO started\n") == "[APP] INFO started\n"


def test_prepend_text_no_trailing_newline():
    t = prepend_text('>> ')
    assert t("INFO started") == ">> INFO started"


def test_append_text_adds_suffix_before_newline():
    t = append_text(' [ok]')
    assert t("INFO started\n") == "INFO started [ok]\n"


def test_append_text_no_trailing_newline():
    t = append_text(' [ok]')
    assert t("INFO started") == "INFO started [ok]"


# ---------------------------------------------------------------------------
# chain
# ---------------------------------------------------------------------------

def test_chain_applies_in_order():
    t = chain(uppercase_level, prepend_text('>> '))
    result = t("info message\n")
    assert result == ">> INFO message\n"


def test_chain_single_transformer():
    t = chain(uppercase_level)
    assert t("debug x\n") == "DEBUG x\n"


# ---------------------------------------------------------------------------
# transform_lines
# ---------------------------------------------------------------------------

def test_transform_lines_applies_to_all():
    lines = ["info a\n", "error b\n", "debug c\n"]
    result = list(transform_lines(lines, uppercase_level))
    assert result == ["INFO a\n", "ERROR b\n", "DEBUG c\n"]


def test_transform_lines_multiple_transformers():
    lines = ["info msg\n"]
    result = list(transform_lines(lines, uppercase_level, append_text(' !!')))
    assert result == ["INFO msg !!\n"]


def test_transform_lines_empty_input():
    assert list(transform_lines([], uppercase_level)) == []
