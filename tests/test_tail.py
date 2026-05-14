"""Tests for logslice.tail and logslice.watcher."""

from __future__ import annotations

import os
import tempfile
import time
import threading
import pytest

from logslice.tail import tail_file
from logslice.watcher import watch_file


@pytest.fixture()
def log_file(tmp_path):
    p = tmp_path / "app.log"
    p.write_text("")  # empty to start
    return p


def _append_lines(path: str, lines: list[str], delay: float = 0.05):
    """Helper: append lines to file after a small delay."""
    time.sleep(delay)
    with open(path, "a") as fh:
        for line in lines:
            fh.write(line)


def test_tail_yields_new_lines(log_file):
    new_lines = [
        "2024-01-01T00:00:01Z INFO hello\n",
        "2024-01-01T00:00:02Z INFO world\n",
    ]
    t = threading.Thread(target=_append_lines, args=(str(log_file), new_lines))
    t.start()
    collected = list(tail_file(str(log_file), poll_interval=0.05, stop_after=2))
    t.join()
    assert collected == new_lines


def test_tail_respects_stop_after(log_file):
    lines = [f"2024-01-01T00:00:0{i}Z INFO msg{i}\n" for i in range(5)]
    t = threading.Thread(target=_append_lines, args=(str(log_file), lines))
    t.start()
    collected = list(tail_file(str(log_file), poll_interval=0.05, stop_after=3))
    t.join()
    assert len(collected) == 3


def test_tail_with_line_parser_filters(log_file):
    lines = [
        "2024-01-01T00:00:01Z DEBUG skip\n",
        "2024-01-01T00:00:02Z INFO keep\n",
    ]

    def only_info(line: str):
        return line if "INFO" in line else None

    t = threading.Thread(target=_append_lines, args=(str(log_file), lines))
    t.start()
    collected = list(
        tail_file(str(log_file), poll_interval=0.05, line_parser=only_info, stop_after=1)
    )
    t.join()
    assert len(collected) == 1
    assert "INFO" in collected[0]


def test_watch_file_basic(log_file):
    new_lines = ["2024-01-01T00:00:01Z INFO watch\n"]
    t = threading.Thread(target=_append_lines, args=(str(log_file), new_lines))
    t.start()
    collected = list(watch_file(str(log_file), poll_interval=0.05, stop_after=1))
    t.join()
    assert collected == new_lines


def test_watch_file_rotation(tmp_path):
    log = tmp_path / "rotating.log"
    log.write_text("")

    rotated_lines = ["2024-01-01T00:00:10Z INFO after-rotation\n"]

    def rotate_and_write():
        time.sleep(0.1)
        log.unlink()
        log.write_text("")  # new inode
        time.sleep(0.05)
        with open(str(log), "a") as fh:
            for line in rotated_lines:
                fh.write(line)

    t = threading.Thread(target=rotate_and_write)
    t.start()
    collected = list(
        watch_file(str(log), poll_interval=0.05, rotation_check_interval=0.1, stop_after=1)
    )
    t.join()
    assert any("after-rotation" in l for l in collected)
