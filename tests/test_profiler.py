"""Tests for logslice.profiler and logslice.cli_profile."""

from __future__ import annotations

import io
import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from logslice.profiler import LogProfile, profile_lines, profile_file
from logslice.cli_profile import build_profile_parser, run_profile


TS = "2024-01-15T10:00:00"
TS2 = "2024-01-15T10:00:10"

SAMPLE_LINES = [
    f"{TS} INFO  service started\n",
    f"{TS} DEBUG loading config\n",
    f"{TS2} ERROR something broke\n",
    f"{TS2} WARN  disk almost full\n",
]


def test_total_lines():
    prof = profile_lines(iter(SAMPLE_LINES))
    assert prof.total_lines == 4


def test_total_bytes():
    prof = profile_lines(iter(SAMPLE_LINES))
    expected = sum(len(l.encode()) for l in SAMPLE_LINES)
    assert prof.total_bytes == expected


def test_first_and_last_timestamp():
    prof = profile_lines(iter(SAMPLE_LINES))
    assert prof.first_timestamp is not None
    assert prof.last_timestamp is not None
    assert prof.first_timestamp <= prof.last_timestamp


def test_duration():
    prof = profile_lines(iter(SAMPLE_LINES))
    assert prof.duration is not None
    assert prof.duration.total_seconds() == pytest.approx(10.0)


def test_lines_per_second():
    prof = profile_lines(iter(SAMPLE_LINES))
    lps = prof.lines_per_second
    assert lps is not None
    assert lps == pytest.approx(0.4)


def test_level_counts():
    prof = profile_lines(iter(SAMPLE_LINES))
    assert prof.level_counts.get("INFO") == 1
    assert prof.level_counts.get("DEBUG") == 1
    assert prof.level_counts.get("ERROR") == 1
    assert prof.level_counts.get("WARN") == 1


def test_empty_input():
    prof = profile_lines(iter([]))
    assert prof.total_lines == 0
    assert prof.duration is None
    assert prof.lines_per_second is None


def test_parse_errors_counted():
    lines = ["no timestamp here\n", "also no timestamp\n"]
    prof = profile_lines(iter(lines))
    assert prof.parse_errors == 2


def test_profile_file(tmp_path: Path):
    log = tmp_path / "app.log"
    log.write_text("".join(SAMPLE_LINES))
    prof = profile_file(str(log))
    assert prof.total_lines == 4
    assert prof.total_bytes == log.stat().st_size


def test_profile_file_missing(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        profile_file(str(tmp_path / "nope.log"))


def test_cli_text_output(tmp_path: Path):
    log = tmp_path / "app.log"
    log.write_text("".join(SAMPLE_LINES))
    parser = build_profile_parser()
    args = parser.parse_args([str(log)])
    out = io.StringIO()
    run_profile(args, out=out)
    text = out.getvalue()
    assert "Total lines" in text
    assert "4" in text


def test_cli_json_output(tmp_path: Path):
    log = tmp_path / "app.log"
    log.write_text("".join(SAMPLE_LINES))
    parser = build_profile_parser()
    args = parser.parse_args(["--format", "json", str(log)])
    out = io.StringIO()
    run_profile(args, out=out)
    data = json.loads(out.getvalue())
    assert data["total_lines"] == 4
    assert "level_counts" in data
