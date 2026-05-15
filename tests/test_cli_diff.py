"""Tests for logslice.cli_diff."""
from __future__ import annotations

import io
import textwrap

import pytest

from logslice.cli_diff import build_diff_parser, run_diff


@pytest.fixture()
def log_files(tmp_path):
    left = tmp_path / "left.log"
    right = tmp_path / "right.log"
    left.write_text("alpha\nbeta\ngamma\n")
    right.write_text("beta\ngamma\ndelta\n")
    return str(left), str(right)


def _make_args(left, right, mode="all", summary=False, no_tag=False):
    parser = build_diff_parser()
    argv = [left, right, "--mode", mode]
    if summary:
        argv.append("--summary")
    if no_tag:
        argv.append("--no-tag")
    return parser.parse_args(argv)


def test_build_diff_parser_returns_parser():
    p = build_diff_parser()
    assert p is not None


def test_build_diff_parser_as_subcommand():
    import argparse
    root = argparse.ArgumentParser()
    sub = root.add_subparsers()
    p = build_diff_parser(sub)
    assert p is not None


def test_run_diff_all_mode(log_files):
    left, right = log_files
    out = io.StringIO()
    args = _make_args(left, right, mode="all")
    run_diff(args, out=out)
    text = out.getvalue()
    assert "< alpha" in text
    assert "> delta" in text
    assert "= beta" in text


def test_run_diff_left_mode(log_files):
    left, right = log_files
    out = io.StringIO()
    args = _make_args(left, right, mode="left")
    run_diff(args, out=out)
    text = out.getvalue()
    assert "alpha" in text
    assert "delta" not in text


def test_run_diff_summary(log_files):
    left, right = log_files
    out = io.StringIO()
    args = _make_args(left, right, summary=True)
    run_diff(args, out=out)
    text = out.getvalue()
    assert "left_only" in text
    assert "right_only" in text
    assert "common" in text


def test_run_diff_no_tag(log_files):
    left, right = log_files
    out = io.StringIO()
    args = _make_args(left, right, mode="all", no_tag=True)
    run_diff(args, out=out)
    for line in out.getvalue().splitlines():
        assert not line.startswith(("< ", "> ", "= "))


def test_run_diff_common_mode(log_files):
    left, right = log_files
    out = io.StringIO()
    args = _make_args(left, right, mode="common")
    run_diff(args, out=out)
    text = out.getvalue()
    assert "beta" in text
    assert "alpha" not in text
    assert "delta" not in text
