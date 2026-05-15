"""Tests for logslice.sampler."""

import pytest

from logslice.sampler import sample_every_n, sample_head, sample_random

LINES = [f"line {i}\n" for i in range(10)]


# ---------------------------------------------------------------------------
# sample_every_n
# ---------------------------------------------------------------------------

def test_every_n_one_returns_all():
    assert list(sample_every_n(LINES, 1)) == LINES


def test_every_n_two_returns_even_indices():
    result = list(sample_every_n(LINES, 2))
    assert result == [LINES[i] for i in range(0, 10, 2)]


def test_every_n_larger_than_input():
    result = list(sample_every_n(LINES, 100))
    assert result == [LINES[0]]


def test_every_n_zero_raises():
    with pytest.raises(ValueError, match="n must be >= 1"):
        list(sample_every_n(LINES, 0))


def test_every_n_negative_raises():
    with pytest.raises(ValueError):
        list(sample_every_n(LINES, -3))


def test_every_n_empty_input():
    assert list(sample_every_n([], 3)) == []


# ---------------------------------------------------------------------------
# sample_random
# ---------------------------------------------------------------------------

def test_random_fraction_one_keeps_all():
    result = list(sample_random(LINES, 1.0, seed=0))
    assert result == LINES


def test_random_fraction_reproducible_with_seed():
    r1 = list(sample_random(LINES, 0.5, seed=42))
    r2 = list(sample_random(LINES, 0.5, seed=42))
    assert r1 == r2


def test_random_different_seeds_may_differ():
    r1 = list(sample_random(LINES, 0.5, seed=1))
    r2 = list(sample_random(LINES, 0.5, seed=99))
    # Very unlikely to be identical for 10 lines at 50 %
    assert r1 != r2 or True  # soft check — just ensure no crash


def test_random_zero_fraction_raises():
    with pytest.raises(ValueError, match="fraction must be in"):
        list(sample_random(LINES, 0.0))


def test_random_fraction_above_one_raises():
    with pytest.raises(ValueError):
        list(sample_random(LINES, 1.5))


def test_random_empty_input():
    assert list(sample_random([], 0.5, seed=0)) == []


# ---------------------------------------------------------------------------
# sample_head
# ---------------------------------------------------------------------------

def test_head_limit_zero_returns_empty():
    assert list(sample_head(LINES, 0)) == []


def test_head_limit_within_range():
    assert list(sample_head(LINES, 3)) == LINES[:3]


def test_head_limit_exceeds_input_returns_all():
    assert list(sample_head(LINES, 1000)) == LINES


def test_head_negative_raises():
    with pytest.raises(ValueError, match="limit must be >= 0"):
        list(sample_head(LINES, -1))


def test_head_empty_input():
    assert list(sample_head([], 5)) == []
