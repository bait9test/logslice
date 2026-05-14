"""Tests for the `logslice tail` CLI sub-command."""

from __future__ import annotations

import argparse
import sys
import threading
import time

import pytest

from logslice.cli_tail import build_tail_parser, run_tail


def _make_args(file: str, **kwargs) -> argparse.Namespace:
    defaults = {
        "file": file,
        "grep_pattern": None,
        "level": None,
        "poll": 0.05,
        "no_rotation": False,
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_run_tail_outputs_lines(tmp_path, capsys):
    log = tmp_path / "app.log"
    log.write_text("")

    def write_lines():
        time.sleep(0.05)
        with open(str(log), "a") as fh:
            fh.write("2024-01-01T00:00:01Z INFO hello\n")
            fh.write("2024-01-01T00:00:02Z INFO world\n")

    # Patch stop_after via monkeypatching watch_file isn't straightforward;
    # instead we rely on KeyboardInterrupt simulation via stop_after in watcher.
    # We'll use a thread + a short-lived watcher by limiting output lines.
    import logslice.watcher as watcher_mod
    original = watcher_mod.watch_file

    def patched_watch(*args, **kwargs):
        kwargs.setdefault("stop_after", 2)
        return original(*args, **kwargs)

    watcher_mod.watch_file = patched_watch
    t = threading.Thread(target=write_lines)
    t.start()
    try:
        result = run_tail(_make_args(str(log)))
    finally:
        watcher_mod.watch_file = original
    t.join()

    captured = capsys.readouterr()
    assert "hello" in captured.out
    assert "world" in captured.out
    assert result == 0


def test_build_tail_parser_defaults():
    root = argparse.ArgumentParser()
    subs = root.add_subparsers()
    build_tail_parser(subs)
    args = root.parse_args(["tail", "myfile.log"])
    assert args.file == "myfile.log"
    assert args.poll == 0.25
    assert args.grep_pattern is None
    assert args.level is None
