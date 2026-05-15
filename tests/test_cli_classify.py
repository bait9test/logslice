"""Tests for logslice.cli_classify."""

import io
import pytest
from logslice.cli_classify import build_classify_parser, run_classify, _parse_rules


def _make_args(**kwargs):
    defaults = {
        "file": "-",
        "rules": [],
        "skip_unmatched": False,
        "stats": False,
    }
    defaults.update(kwargs)
    import argparse
    ns = argparse.Namespace(**defaults)
    return ns


def _run(lines, **kwargs):
    import tempfile, os
    content = "".join(lines)
    with tempfile.NamedTemporaryFile(mode="w", suffix=".log", delete=False) as f:
        f.write(content)
        name = f.name
    try:
        args = _make_args(file=name, **kwargs)
        out, err = io.StringIO(), io.StringIO()
        run_classify(args, out=out, err=err)
        return out.getvalue(), err.getvalue()
    finally:
        os.unlink(name)


def test_build_classify_parser_returns_parser():
    p = build_classify_parser()
    assert p is not None


def test_build_classify_parser_as_subcommand():
    import argparse
    root = argparse.ArgumentParser()
    sub = root.add_subparsers()
    p = build_classify_parser(sub)
    assert p is not None


def test_parse_rules_valid():
    rules = _parse_rules(["error:ERROR", "warn:WARN"])
    assert rules[0].name == "error"
    assert rules[1].name == "warn"


def test_parse_rules_invalid_raises():
    with pytest.raises(ValueError, match="NAME:PATTERN"):
        _parse_rules(["badformat"])


def test_run_classify_tags_lines():
    lines = ["2024-01-01 ERROR disk full\n", "2024-01-01 INFO started\n"]
    out, _ = _run(lines, rules=["error:ERROR", "info:INFO"])
    assert "[error]" in out
    assert "[info]" in out


def test_run_classify_unmatched_tagged_with_question_mark():
    lines = ["2024-01-01 DEBUG trace\n"]
    out, _ = _run(lines, rules=["error:ERROR"])
    assert "[?]" in out


def test_run_classify_skip_unmatched():
    lines = ["ERROR here\n", "DEBUG there\n"]
    out, _ = _run(lines, rules=["error:ERROR"], skip_unmatched=True)
    assert "[error]" in out
    assert "[?]" not in out
    assert "DEBUG" not in out


def test_run_classify_stats_written_to_err():
    lines = ["ERROR a\n", "ERROR b\n", "DEBUG c\n"]
    _, err = _run(lines, rules=["error:ERROR"], stats=True)
    assert "error: 2" in err
    assert "__unmatched__: 1" in err


def test_run_classify_no_rules_all_unmatched():
    lines = ["anything\n"]
    out, _ = _run(lines)
    assert "[?]" in out
