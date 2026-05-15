"""Integration tests: classifier wired with filters and formatter."""

from logslice.classifier import Rule, classify_lines, category_counts
from logslice.filters import grep, filter_level, pipeline
from logslice.formatter import format_raw


LINES = [
    "2024-06-01T10:00:00 ERROR connection refused\n",
    "2024-06-01T10:00:01 WARNING retry attempt 1\n",
    "2024-06-01T10:00:02 INFO heartbeat ok\n",
    "2024-06-01T10:00:03 DEBUG verbose trace\n",
    "2024-06-01T10:00:04 ERROR timeout reached\n",
]

RULES = [
    Rule.from_str("error", r"\berror\b"),
    Rule.from_str("warning", r"\bwarn(ing)?\b"),
    Rule.from_str("info", r"\binfo\b"),
]


def test_classify_then_count_by_category():
    classified = list(classify_lines(LINES, RULES))
    counts = category_counts(classified)
    assert counts["error"] == 2
    assert counts["warning"] == 1
    assert counts["info"] == 1
    assert counts["__unmatched__"] == 1


def test_classify_skip_unmatched_drops_debug():
    classified = list(classify_lines(LINES, RULES, skip_unmatched=True))
    bodies = [c.line for c in classified]
    assert all("DEBUG" not in b for b in bodies)
    assert len(classified) == 4


def test_classify_after_grep_filter():
    grepped = list(grep(LINES, "connection|timeout"))
    classified = list(classify_lines(grepped, RULES))
    assert all(c.category == "error" for c in classified)
    assert len(classified) == 2


def test_classify_preserves_original_line():
    classified = list(classify_lines(LINES, RULES))
    for original, result in zip(LINES, classified):
        assert result.line == original


def test_category_counts_only_errors():
    error_lines = [l for l in LINES if "ERROR" in l]
    classified = classify_lines(error_lines, RULES)
    counts = category_counts(classified)
    assert counts.get("error", 0) == 2
    assert "warning" not in counts
