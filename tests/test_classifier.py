"""Tests for logslice.classifier."""

import pytest
from logslice.classifier import (
    Rule,
    ClassifiedLine,
    classify_line,
    classify_lines,
    category_counts,
)


@pytest.fixture()
def rules():
    return [
        Rule.from_str("error", r"\berror\b"),
        Rule.from_str("warning", r"\bwarn(ing)?\b"),
        Rule.from_str("info", r"\binfo\b"),
    ]


def test_rule_from_str_compiles(rules):
    assert rules[0].name == "error"
    assert rules[0].pattern.search("an ERROR occurred")


def test_classify_line_first_match(rules):
    result = classify_line("ERROR: disk full", rules)
    assert result.category == "error"
    assert result.line == "ERROR: disk full"


def test_classify_line_second_rule(rules):
    result = classify_line("WARNING: low memory", rules)
    assert result.category == "warning"


def test_classify_line_no_match(rules):
    result = classify_line("DEBUG: all good", rules)
    assert result.category is None


def test_classify_line_case_insensitive(rules):
    assert classify_line("Info: started", rules).category == "info"


def test_classify_lines_all_matched(rules):
    lines = ["error here", "warn there", "info note"]
    results = list(classify_lines(lines, rules))
    assert [r.category for r in results] == ["error", "warning", "info"]


def test_classify_lines_includes_unmatched_by_default(rules):
    lines = ["debug msg", "error msg"]
    results = list(classify_lines(lines, rules))
    assert results[0].category is None
    assert results[1].category == "error"


def test_classify_lines_skip_unmatched(rules):
    lines = ["debug msg", "error msg", "trace msg"]
    results = list(classify_lines(lines, rules, skip_unmatched=True))
    assert len(results) == 1
    assert results[0].category == "error"


def test_category_counts(rules):
    lines = ["error a", "error b", "warn c", "debug d"]
    classified = classify_lines(lines, rules)
    counts = category_counts(classified)
    assert counts["error"] == 2
    assert counts["warning"] == 1
    assert counts["__unmatched__"] == 1


def test_category_counts_empty():
    assert category_counts([]) == {}


def test_classify_lines_empty_rules():
    lines = ["anything"]
    results = list(classify_lines(lines, []))
    assert results[0].category is None


def test_category_counts_no_unmatched(rules):
    """When all lines match a rule, __unmatched__ should not appear in counts."""
    lines = ["error here", "info there"]
    classified = classify_lines(lines, rules)
    counts = category_counts(classified)
    assert "__unmatched__" not in counts
    assert counts["error"] == 1
    assert counts["info"] == 1
