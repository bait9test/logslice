"""Summarize a stream of log lines into a compact human-readable report."""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field
from typing import Iterable, List, Optional

_LEVEL_RE = re.compile(r"\b(DEBUG|INFO|WARN(?:ING)?|ERROR|CRITICAL|FATAL)\b", re.IGNORECASE)
_TS_RE = re.compile(r"^(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2})")


@dataclass
class LogSummary:
    total_lines: int = 0
    level_counts: Counter = field(default_factory=Counter)
    first_timestamp: Optional[str] = None
    last_timestamp: Optional[str] = None
    top_terms: List[tuple] = field(default_factory=list)


def _extract_level(line: str) -> Optional[str]:
    m = _LEVEL_RE.search(line)
    if m:
        lvl = m.group(1).upper()
        return "WARN" if lvl == "WARNING" else lvl
    return None


def _extract_timestamp(line: str) -> Optional[str]:
    m = _TS_RE.match(line.strip())
    return m.group(1) if m else None


def _tokenize(line: str) -> List[str]:
    """Return meaningful word tokens from a log line (skip timestamps, punctuation)."""
    # drop leading timestamp
    body = _TS_RE.sub("", line).strip()
    tokens = re.findall(r"[a-zA-Z][a-zA-Z0-9_]{3,}", body)
    return [t.lower() for t in tokens]


_STOP = frozenset(
    {"info", "warn", "error", "debug", "fatal", "critical", "warning",
     "true", "false", "none", "null", "from", "with", "this", "that"}
)


def summarize_lines(lines: Iterable[str], top_n: int = 5) -> LogSummary:
    """Consume *lines* and return a :class:`LogSummary`."""
    summary = LogSummary()
    term_counter: Counter = Counter()

    for line in lines:
        summary.total_lines += 1

        lvl = _extract_level(line)
        if lvl:
            summary.level_counts[lvl] += 1

        ts = _extract_timestamp(line)
        if ts:
            if summary.first_timestamp is None:
                summary.first_timestamp = ts
            summary.last_timestamp = ts

        for token in _tokenize(line):
            if token not in _STOP:
                term_counter[token] += 1

    summary.top_terms = term_counter.most_common(top_n)
    return summary


def format_summary(s: LogSummary) -> str:
    """Return a multi-line human-readable summary string."""
    lines = [
        f"Lines      : {s.total_lines}",
        f"First      : {s.first_timestamp or 'n/a'}",
        f"Last       : {s.last_timestamp or 'n/a'}",
        "Levels     : "
        + ", ".join(f"{lvl}={cnt}" for lvl, cnt in sorted(s.level_counts.items()))
        if s.level_counts else "Levels     : n/a",
        "Top terms  : "
        + ", ".join(f"{t}({c})" for t, c in s.top_terms)
        if s.top_terms else "Top terms  : n/a",
    ]
    return "\n".join(lines) + "\n"
