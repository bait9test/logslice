"""Tests for logslice.stats."""

from logslice.stats import collect_stats, summarise, SliceStats


SAMPLE_LINES = [
    "2024-01-01T00:00:01Z INFO  server started\n",
    "2024-01-01T00:00:02Z DEBUG request received\n",
    "2024-01-01T00:00:03Z ERROR something broke\n",
    "2024-01-01T00:00:04Z INFO  request completed\n",
    "2024-01-01T00:00:05Z WARN  slow response\n",
]


def test_total_lines():
    stats = collect_stats(SAMPLE_LINES)
    assert stats.total_lines == 5


def test_bytes_read():
    stats = collect_stats(SAMPLE_LINES)
    expected = sum(len(l.encode("utf-8")) for l in SAMPLE_LINES)
    assert stats.bytes_read == expected


def test_level_counts():
    stats = collect_stats(SAMPLE_LINES)
    assert stats.level_counts["INFO"] == 2
    assert stats.level_counts["DEBUG"] == 1
    assert stats.level_counts["ERROR"] == 1
    assert stats.level_counts["WARN"] == 1


def test_first_and_last_timestamp():
    stats = collect_stats(SAMPLE_LINES)
    assert stats.first_timestamp == "2024-01-01T00:00:01Z"
    assert stats.last_timestamp == "2024-01-01T00:00:05Z"


def test_empty_input():
    stats = collect_stats([])
    assert stats.total_lines == 0
    assert stats.bytes_read == 0
    assert stats.first_timestamp is None
    assert stats.last_timestamp is None


def test_unknown_level_counted():
    lines = ["2024-01-01T00:00:01Z nodateline\n"]
    stats = collect_stats(lines)
    assert stats.level_counts.get("UNKNOWN", 0) >= 1


def test_as_dict_keys():
    stats = collect_stats(SAMPLE_LINES)
    d = stats.as_dict()
    assert set(d.keys()) == {
        "total_lines", "level_counts", "first_timestamp", "last_timestamp", "bytes_read"
    }


def test_summarise_contains_counts():
    stats = collect_stats(SAMPLE_LINES)
    summary = summarise(stats)
    assert "5" in summary
    assert "INFO" in summary
    assert "ERROR" in summary


def test_summarise_na_when_no_timestamps():
    stats = SliceStats()
    summary = summarise(stats)
    assert "n/a" in summary
