"""Tests for logslice.paginator."""

import pytest

from logslice.paginator import iter_pages, paginate


LINES = [f"line {i}" for i in range(1, 11)]  # 10 lines


# ---------------------------------------------------------------------------
# paginate()
# ---------------------------------------------------------------------------

def test_paginate_first_page():
    page, total = paginate(LINES, page_size=3, page_number=1)
    assert page == ["line 1", "line 2", "line 3"]
    assert total == 4  # ceil(10/3)


def test_paginate_last_partial_page():
    page, total = paginate(LINES, page_size=3, page_number=4)
    assert page == ["line 10"]
    assert total == 4


def test_paginate_middle_page():
    page, total = paginate(LINES, page_size=4, page_number=2)
    assert page == ["line 5", "line 6", "line 7", "line 8"]
    assert total == 3  # ceil(10/4)


def test_paginate_page_beyond_total_returns_empty():
    page, total = paginate(LINES, page_size=5, page_number=99)
    assert page == []
    assert total == 2


def test_paginate_empty_input():
    page, total = paginate([], page_size=5, page_number=1)
    assert page == []
    assert total == 0


def test_paginate_exact_fit():
    page, total = paginate(LINES, page_size=5, page_number=2)
    assert page == ["line 6", "line 7", "line 8", "line 9", "line 10"]
    assert total == 2


def test_paginate_invalid_page_size():
    with pytest.raises(ValueError, match="page_size"):
        paginate(LINES, page_size=0)


def test_paginate_invalid_page_number():
    with pytest.raises(ValueError, match="page_number"):
        paginate(LINES, page_size=5, page_number=0)


# ---------------------------------------------------------------------------
# iter_pages()
# ---------------------------------------------------------------------------

def test_iter_pages_yields_all_chunks():
    pages = list(iter_pages(LINES, page_size=3))
    assert len(pages) == 4
    assert pages[0] == ["line 1", "line 2", "line 3"]
    assert pages[-1] == ["line 10"]


def test_iter_pages_exact_multiple():
    pages = list(iter_pages(LINES, page_size=5))
    assert len(pages) == 2
    assert pages[1] == ["line 6", "line 7", "line 8", "line 9", "line 10"]


def test_iter_pages_single_line_per_page():
    pages = list(iter_pages(["a", "b", "c"], page_size=1))
    assert pages == [["a"], ["b"], ["c"]]


def test_iter_pages_empty_input_yields_nothing():
    pages = list(iter_pages([], page_size=5))
    assert pages == []


def test_iter_pages_invalid_page_size():
    with pytest.raises(ValueError, match="page_size"):
        list(iter_pages(LINES, page_size=-1))
