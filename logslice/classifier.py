"""Classify log lines into named categories based on pattern rules."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Iterable, Iterator, Optional


@dataclass
class Rule:
    """A named classification rule backed by a compiled regex."""
    name: str
    pattern: re.Pattern

    @classmethod
    def from_str(cls, name: str, pattern: str, flags: int = re.IGNORECASE) -> "Rule":
        return cls(name=name, pattern=re.compile(pattern, flags))


@dataclass
class ClassifiedLine:
    """A log line together with its matched category (or None)."""
    line: str
    category: Optional[str] = None


def classify_line(line: str, rules: list[Rule]) -> ClassifiedLine:
    """Return the first matching rule's name, or None if no rule matches."""
    for rule in rules:
        if rule.pattern.search(line):
            return ClassifiedLine(line=line, category=rule.name)
    return ClassifiedLine(line=line, category=None)


def classify_lines(
    lines: Iterable[str],
    rules: list[Rule],
    *,
    skip_unmatched: bool = False,
) -> Iterator[ClassifiedLine]:
    """Classify every line; optionally drop lines that match no rule."""
    for line in lines:
        result = classify_line(line, rules)
        if skip_unmatched and result.category is None:
            continue
        yield result


def category_counts(classified: Iterable[ClassifiedLine]) -> dict[str, int]:
    """Count how many lines belong to each category."""
    counts: dict[str, int] = {}
    for item in classified:
        key = item.category or "__unmatched__"
        counts[key] = counts.get(key, 0) + 1
    return counts
