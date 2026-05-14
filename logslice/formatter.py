"""Output formatting for log slices."""

import json
import sys
from typing import Iterable, TextIO


FORMAT_RAW = "raw"
FORMAT_JSON = "json"
FORMAT_JSONL = "jsonl"
FORMAT_CSV = "csv"

SUPPORTED_FORMATS = (FORMAT_RAW, FORMAT_JSON, FORMAT_JSONL, FORMAT_CSV)


def _parse_line_to_dict(line: str) -> dict:
    """Best-effort parse of a log line into a dict with 'timestamp' and 'message'."""
    line = line.rstrip("\n")
    parts = line.split(" ", 1)
    if len(parts) == 2:
        return {"timestamp": parts[0], "message": parts[1]}
    return {"timestamp": "", "message": line}


def format_raw(lines: Iterable[str], out: TextIO = sys.stdout) -> None:
    """Write lines as-is."""
    for line in lines:
        out.write(line if line.endswith("\n") else line + "\n")


def format_jsonl(lines: Iterable[str], out: TextIO = sys.stdout) -> None:
    """Write each line as a JSON object on its own line."""
    for line in lines:
        record = _parse_line_to_dict(line)
        out.write(json.dumps(record) + "\n")


def format_json(lines: Iterable[str], out: TextIO = sys.stdout) -> None:
    """Write all lines as a JSON array."""
    records = [_parse_line_to_dict(line) for line in lines]
    json.dump(records, out, indent=2)
    out.write("\n")


def format_csv(lines: Iterable[str], out: TextIO = sys.stdout) -> None:
    """Write lines as CSV with 'timestamp,message' columns."""
    import csv
    writer = csv.writer(out)
    writer.writerow(["timestamp", "message"])
    for line in lines:
        record = _parse_line_to_dict(line)
        writer.writerow([record["timestamp"], record["message"]])


def write_output(
    lines: Iterable[str],
    fmt: str = FORMAT_RAW,
    out: TextIO = sys.stdout,
) -> None:
    """Dispatch to the appropriate formatter."""
    if fmt == FORMAT_RAW:
        format_raw(lines, out)
    elif fmt == FORMAT_JSONL:
        format_jsonl(lines, out)
    elif fmt == FORMAT_JSON:
        format_json(lines, out)
    elif fmt == FORMAT_CSV:
        format_csv(lines, out)
    else:
        raise ValueError(f"Unsupported format: {fmt!r}. Choose from {SUPPORTED_FORMATS}")
