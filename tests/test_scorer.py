"""Tests for logslice.scorer."""

import pytest

from logslice.scorer import (
    _score_line,
    filter_by_score,
    score_lines,
    top_scored,
)

WEIGHTS = {"error": 3.0, "warn": 1.5, "timeout": 2.0}


# --- _score_line ---

def test_score_line_single_match():
    assert _score_line("ERROR: disk full", WEIGHTS) == 3.0


def test_score_line_multiple_terms():
    score = _score_line("error timeout occurred", WEIGHTS)
    assert score == pytest.approx(5.0)


def test_score_line_repeated_term():
    score = _score_line("error error error", WEIGHTS)
    assert score == pytest.approx(9.0)


def test_score_line_case_insensitive():
    assert _score_line("WARN: something", WEIGHTS) == pytest.approx(1.5)


def test_score_line_no_match_returns_zero():
    assert _score_line("everything is fine", WEIGHTS) == 0.0


def test_score_line_empty_line():
    assert _score_line("", WEIGHTS) == 0.0


def test_score_line_empty_weights():
    assert _score_line("error warn timeout", {}) == 0.0


# --- score_lines ---

def test_score_lines_yields_all():
    lines = ["error here", "all good", "warn: low disk"]
    results = list(score_lines(lines, WEIGHTS))
    assert len(results) == 3


def test_score_lines_zero_score_included():
    results = list(score_lines(["nothing special"], WEIGHTS))
    assert results[0][0] == 0.0


def test_score_lines_correct_values():
    results = list(score_lines(["error", "warn", "info"], WEIGHTS))
    scores = [s for s, _ in results]
    assert scores == pytest.approx([3.0, 1.5, 0.0])


# --- top_scored ---

def test_top_scored_returns_sorted_descending():
    lines = ["warn msg", "error critical", "info ok", "timeout reached"]
    top = top_scored(lines, WEIGHTS, n=3)
    scores = [s for s, _ in top]
    assert scores == sorted(scores, reverse=True)


def test_top_scored_respects_n():
    lines = ["error a", "error b", "error c", "error d"]
    assert len(top_scored(lines, WEIGHTS, n=2)) == 2


def test_top_scored_min_score_filters():
    lines = ["info only", "error big"]
    top = top_scored(lines, WEIGHTS, n=10, min_score=1.0)
    assert all(s >= 1.0 for s, _ in top)
    assert len(top) == 1


def test_top_scored_invalid_n_raises():
    with pytest.raises(ValueError):
        top_scored(["line"], WEIGHTS, n=0)


# --- filter_by_score ---

def test_filter_by_score_keeps_matching():
    lines = ["error now", "all fine", "warn low"]
    result = list(filter_by_score(lines, WEIGHTS, threshold=1.5))
    assert "error now" in result
    assert "warn low" in result
    assert "all fine" not in result


def test_filter_by_score_zero_threshold_keeps_all():
    lines = ["a", "b", "c"]
    assert list(filter_by_score(lines, WEIGHTS, threshold=0.0)) == lines


def test_filter_by_score_negative_threshold_raises():
    with pytest.raises(ValueError):
        list(filter_by_score(["line"], WEIGHTS, threshold=-1.0))
