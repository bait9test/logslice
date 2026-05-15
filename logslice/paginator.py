"""Paginator: split a stream of log lines into fixed-size pages."""

from __future__ import annotations

from typing import Iterable, Iterator, List, Tuple


def paginate(
    lines: Iterable[str],
    page_size: int,
    page_number: int = 1,
) -> Tuple[List[str], int]:
    """Return a single page of lines and the total page count.

    Args:
        lines:       Iterable of log lines (consumed once).
        page_size:   Number of lines per page.  Must be >= 1.
        page_number: 1-based page index to return.  Must be >= 1.

    Returns:
        A tuple of (page_lines, total_pages).
        *page_lines* is an empty list when *page_number* exceeds total pages.
    """
    if page_size < 1:
        raise ValueError(f"page_size must be >= 1, got {page_size}")
    if page_number < 1:
        raise ValueError(f"page_number must be >= 1, got {page_number}")

    all_lines: List[str] = list(lines)
    total = len(all_lines)
    if total == 0:
        return [], 0

    total_pages = (total + page_size - 1) // page_size
    start = (page_number - 1) * page_size
    end = start + page_size
    return all_lines[start:end], total_pages


def iter_pages(
    lines: Iterable[str],
    page_size: int,
) -> Iterator[List[str]]:
    """Yield successive pages of *page_size* lines each.

    Args:
        lines:     Iterable of log lines.
        page_size: Number of lines per page.  Must be >= 1.
    """
    if page_size < 1:
        raise ValueError(f"page_size must be >= 1, got {page_size}")

    page: List[str] = []
    for line in lines:
        page.append(line)
        if len(page) == page_size:
            yield page
            page = []
    if page:
        yield page
