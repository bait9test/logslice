"""Tests for logslice.compressor."""

from __future__ import annotations

import os
import tempfile

import pytest

from logslice.compressor import (
    compress_lines,
    compress_to_file,
    decompress_from_file,
    decompress_lines,
)


SAMPLE = [
    "2024-01-01T00:00:01Z INFO  server started\n",
    "2024-01-01T00:00:02Z DEBUG request received\n",
    "2024-01-01T00:00:03Z ERROR something went wrong\n",
]


def test_compress_then_decompress_roundtrip():
    data = compress_lines(SAMPLE)
    result = list(decompress_lines(data))
    assert result == SAMPLE


def test_compress_adds_newline_if_missing():
    lines = ["no newline here"]
    data = compress_lines(lines)
    result = list(decompress_lines(data))
    assert result == ["no newline here\n"]


def test_compress_empty_iterable():
    data = compress_lines([])
    assert isinstance(data, bytes)
    result = list(decompress_lines(data))
    assert result == []


def test_compress_level_produces_bytes():
    for level in (1, 6, 9):
        data = compress_lines(SAMPLE, level=level)
        assert len(data) > 0
        assert list(decompress_lines(data)) == SAMPLE


def test_decompress_lines_preserves_newlines():
    data = compress_lines(SAMPLE)
    for line in decompress_lines(data):
        assert line.endswith("\n")


def test_compress_to_file_returns_line_count(tmp_path):
    path = str(tmp_path / "out.log.gz")
    count = compress_to_file(SAMPLE, path)
    assert count == len(SAMPLE)


def test_compress_to_file_creates_file(tmp_path):
    path = str(tmp_path / "out.log.gz")
    compress_to_file(SAMPLE, path)
    assert os.path.exists(path)
    assert os.path.getsize(path) > 0


def test_decompress_from_file_roundtrip(tmp_path):
    path = str(tmp_path / "out.log.gz")
    compress_to_file(SAMPLE, path)
    result = list(decompress_from_file(path))
    assert result == SAMPLE


def test_decompress_from_file_empty(tmp_path):
    path = str(tmp_path / "empty.log.gz")
    compress_to_file([], path)
    result = list(decompress_from_file(path))
    assert result == []


def test_compress_to_file_adds_newline_if_missing(tmp_path):
    path = str(tmp_path / "nonl.log.gz")
    compress_to_file(["no newline"], path)
    result = list(decompress_from_file(path))
    assert result == ["no newline\n"]
