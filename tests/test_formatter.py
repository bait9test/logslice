"""Tests for logslice.formatter."""

import io
import json
import csv
import pytest

from logslice.formatter import (
    write_output,
    FORMAT_RAW,
    FORMAT_JSON,
    FORMAT_JSONL,
    FORMAT_CSV,
)

SAMPLE_LINES = [
    "2024-01-01T00:00:01Z server started\n",
    "2024-01-01T00:00:02Z request received\n",
    "2024-01-01T00:00:03Z request completed\n",
]


def test_format_raw():
    out = io.StringIO()
    write_output(SAMPLE_LINES, fmt=FORMAT_RAW, out=out)
    assert out.getvalue() == "".join(SAMPLE_LINES)


def test_format_raw_adds_newline_if_missing():
    out = io.StringIO()
    write_output(["2024-01-01T00:00:01Z no newline"], fmt=FORMAT_RAW, out=out)
    assert out.getvalue().endswith("\n")


def test_format_jsonl():
    out = io.StringIO()
    write_output(SAMPLE_LINES, fmt=FORMAT_JSONL, out=out)
    records = [json.loads(l) for l in out.getvalue().strip().splitlines()]
    assert len(records) == 3
    assert records[0]["timestamp"] == "2024-01-01T00:00:01Z"
    assert records[0]["message"] == "server started"


def test_format_json_is_array():
    out = io.StringIO()
    write_output(SAMPLE_LINES, fmt=FORMAT_JSON, out=out)
    data = json.loads(out.getvalue())
    assert isinstance(data, list)
    assert len(data) == 3
    assert data[1]["timestamp"] == "2024-01-01T00:00:02Z"


def test_format_csv_has_header():
    out = io.StringIO()
    write_output(SAMPLE_LINES, fmt=FORMAT_CSV, out=out)
    out.seek(0)
    reader = csv.reader(out)
    rows = list(reader)
    assert rows[0] == ["timestamp", "message"]
    assert len(rows) == 4  # header + 3 lines
    assert rows[1][0] == "2024-01-01T00:00:01Z"


def test_format_unknown_raises():
    out = io.StringIO()
    with pytest.raises(ValueError, match="Unsupported format"):
        write_output(SAMPLE_LINES, fmt="xml", out=out)


def test_format_empty_lines():
    out = io.StringIO()
    write_output([], fmt=FORMAT_JSON, out=out)
    data = json.loads(out.getvalue())
    assert data == []


def test_format_line_without_space():
    out = io.StringIO()
    write_output(["nodateline\n"], fmt=FORMAT_JSONL, out=out)
    record = json.loads(out.getvalue())
    assert record["timestamp"] == ""
    assert record["message"] == "nodateline"
