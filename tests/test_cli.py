"""Tests for logslice.cli."""

import os
from datetime import datetime

import pytest

from logslice.cli import main


LOG_LINES = [
    "2024-01-01T10:00:00 INFO  startup",
    "2024-01-01T10:01:00 DEBUG config",
    "2024-01-01T10:02:00 INFO  request",
    "2024-01-01T10:03:00 WARN  slow",
    "2024-01-01T10:04:00 ERROR timeout",
]


@pytest.fixture()
def log_file(tmp_path):
    path = tmp_path / "app.log"
    path.write_text("\n".join(LOG_LINES) + "\n", encoding="utf-8")
    return str(path)


def test_cli_basic_slice(log_file, capsys):
    rc = main([log_file, "2024-01-01T10:01:00", "2024-01-01T10:02:00"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "config" in out
    assert "request" in out
    assert "startup" not in out


def test_cli_invalid_start(log_file, capsys):
    rc = main([log_file, "not-a-date", "2024-01-01T10:00:00"])
    assert rc == 1
    assert "invalid timestamp" in capsys.readouterr().err


def test_cli_start_after_end(log_file, capsys):
    rc = main([log_file, "2024-01-01T11:00:00", "2024-01-01T10:00:00"])
    assert rc == 1
    assert "start timestamp" in capsys.readouterr().err


def test_cli_missing_file(capsys):
    rc = main(["/nonexistent/path.log", "2024-01-01T10:00:00", "2024-01-01T11:00:00"])
    assert rc == 1
    assert "file not found" in capsys.readouterr().err


def test_cli_output_file(log_file, tmp_path):
    out_path = str(tmp_path / "out.log")
    rc = main([log_file, "2024-01-01T10:00:00", "2024-01-01T10:01:00", "-o", out_path])
    assert rc == 0
    content = open(out_path).read()
    assert "startup" in content
    assert "config" in content
    assert "request" not in content
