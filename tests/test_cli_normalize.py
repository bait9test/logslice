"""Tests for logslice.cli_normalize."""

from __future__ import annotations

import argparse
import io

import pytest

from logslice.cli_normalize import build_normalize_parser, run_normalize


def _make_args(**kwargs) -> argparse.Namespace:
    defaults = dict(file=None, fix_level=True, fix_whitespace=True)
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def _run(lines: list[str], **kwargs) -> str:
    """Run normalize over *lines* and return captured output."""
    out = io.StringIO()
    # Write lines to a temp file-like and monkeypatch stdin path via file arg
    import tempfile, os

    with tempfile.NamedTemporaryFile(mode="w", suffix=".log", delete=False) as f:
        f.writelines(lines)
        name = f.name

    try:
        args = _make_args(file=name, **kwargs)
        run_normalize(args, out=out)
    finally:
        os.unlink(name)

    return out.getvalue()


def test_build_normalize_parser_returns_parser():
    p = build_normalize_parser()
    assert isinstance(p, argparse.ArgumentParser)


def test_build_normalize_parser_as_subcommand():
    root = argparse.ArgumentParser()
    sub = root.add_subparsers()
    p = build_normalize_parser(parent=sub)
    assert isinstance(p, argparse.ArgumentParser)


def test_run_normalize_canonicalizes_level():
    result = _run(["warn: disk full\n"])
    assert "WARNING" in result
    assert "warn:" not in result


def test_run_normalize_collapses_whitespace():
    result = _run(["info   too   many   spaces\n"])
    assert "  " not in result


def test_run_normalize_no_level_flag():
    result = _run(["warn message\n"], fix_level=False)
    assert "warn" in result
    assert "WARNING" not in result


def test_run_normalize_no_whitespace_flag():
    result = _run(["info   spaced\n"], fix_whitespace=False)
    assert "   " in result


def test_run_normalize_adds_newline_if_missing():
    result = _run(["err no newline"])
    assert result.endswith("\n")


def test_run_normalize_empty_file():
    result = _run([])
    assert result == ""
