"""Tests for logslice.cli_annotate."""
from __future__ import annotations

import argparse
import io

import pytest

from logslice.cli_annotate import build_annotate_parser, run_annotate


def _make_args(**kwargs) -> argparse.Namespace:
    defaults = dict(file=None, sequence=True, offset=False, start=1, prefix="", suffix=" ")
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def _run(lines: list[str], **kwargs) -> list[str]:
    """Write *lines* to a temp file, run annotate, return output lines."""
    import tempfile, os
    with tempfile.NamedTemporaryFile(mode="w", suffix=".log", delete=False) as f:
        f.writelines(lines)
        name = f.name
    try:
        args = _make_args(file=name, **kwargs)
        out = io.StringIO()
        run_annotate(args, out=out)
        return out.getvalue().splitlines(keepends=True)
    finally:
        os.unlink(name)


# ---------------------------------------------------------------------------
# parser construction
# ---------------------------------------------------------------------------

def test_build_annotate_parser_returns_parser():
    p = build_annotate_parser()
    assert isinstance(p, argparse.ArgumentParser)


def test_build_annotate_parser_as_subcommand():
    root = argparse.ArgumentParser()
    sub = root.add_subparsers()
    p = build_annotate_parser(parent=sub)
    assert p is not None


# ---------------------------------------------------------------------------
# sequence mode (default)
# ---------------------------------------------------------------------------

def test_sequence_numbers_prepended():
    result = _run(["alpha\n", "bravo\n"])
    assert result[0].startswith("1 ")
    assert result[1].startswith("2 ")


def test_sequence_custom_start():
    result = _run(["x\n", "y\n"], start=5)
    assert result[0].startswith("5 ")
    assert result[1].startswith("6 ")


def test_sequence_prefix_suffix():
    result = _run(["hello\n"], prefix="[", suffix="] ")
    assert result[0].startswith("[1] ")


def test_sequence_body_preserved():
    result = _run(["important log line\n"])
    assert "important log line" in result[0]


# ---------------------------------------------------------------------------
# offset mode
# ---------------------------------------------------------------------------

def test_offset_first_line_zero():
    result = _run(["abc\n"], offset=True, start=0)
    assert result[0].startswith("0 ")


def test_offset_second_line_advances():
    result = _run(["ab\n", "cd\n"], offset=True, start=0)
    first_offset = int(result[0].split()[0])
    second_offset = int(result[1].split()[0])
    assert second_offset == first_offset + len("ab\n".encode())


def test_offset_body_preserved():
    result = _run(["payload\n"], offset=True, start=0)
    assert "payload" in result[0]
