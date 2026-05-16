"""Tests for logslice.enricher."""
import pytest

from logslice.enricher import (
    enrich_field,
    enrich_host,
    enrich_pipeline,
    enrich_with,
)


def _lines(*texts):
    return list(texts)


# ---------------------------------------------------------------------------
# enrich_host
# ---------------------------------------------------------------------------

def test_enrich_host_appends_host_tag():
    result = list(enrich_host(["2024-01-01 INFO hello"], hostname="testbox"))
    assert result == ["2024-01-01 INFO hello host=testbox"]


def test_enrich_host_preserves_newline():
    result = list(enrich_host(["2024-01-01 INFO hello\n"], hostname="box"))
    assert result == ["2024-01-01 INFO hello host=box\n"]


def test_enrich_host_multiple_lines():
    lines = ["line one\n", "line two\n"]
    result = list(enrich_host(lines, hostname="srv"))
    assert all("host=srv" in r for r in result)
    assert len(result) == 2


# ---------------------------------------------------------------------------
# enrich_field
# ---------------------------------------------------------------------------

def test_enrich_field_appends_kv():
    result = list(enrich_field(["msg"], key="env", value="prod"))
    assert result == ["msg env=prod"]


def test_enrich_field_preserves_newline():
    result = list(enrich_field(["msg\n"], key="run", value="42"))
    assert result == ["msg run=42\n"]


def test_enrich_field_empty_key_raises():
    with pytest.raises(ValueError, match="key must not be empty"):
        list(enrich_field(["msg"], key="", value="x"))


def test_enrich_field_empty_value_allowed():
    result = list(enrich_field(["msg"], key="tag", value=""))
    assert result == ["msg tag="]


# ---------------------------------------------------------------------------
# enrich_with
# ---------------------------------------------------------------------------

def test_enrich_with_custom_fn():
    fn = lambda line: "custom=yes" if "ERROR" in line else ""
    lines = ["INFO ok\n", "ERROR bad\n"]
    result = list(enrich_with(lines, fn))
    assert "custom=yes" in result[1]
    assert "custom=yes" not in result[0]


def test_enrich_with_empty_suffix_leaves_line_unchanged():
    result = list(enrich_with(["plain line"], fn=lambda l: ""))
    assert result == ["plain line"]


# ---------------------------------------------------------------------------
# enrich_pipeline
# ---------------------------------------------------------------------------

def test_enrich_pipeline_chains_enrichers():
    from functools import partial

    add_host = partial(enrich_host, hostname="h1")
    add_env = partial(enrich_field, key="env", value="staging")

    result = list(enrich_pipeline(["msg"], add_host, add_env))
    assert "host=h1" in result[0]
    assert "env=staging" in result[0]


def test_enrich_pipeline_empty_enrichers_passthrough():
    lines = ["a\n", "b\n"]
    result = list(enrich_pipeline(lines))
    assert result == lines
