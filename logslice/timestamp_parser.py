"""Utilities for parsing timestamps from log lines."""

import re
from datetime import datetime
from typing import Optional

# Common log timestamp patterns ordered by specificity
TIMESTAMP_PATTERNS = [
    # ISO 8601: 2024-01-15T13:45:22.123456
    (r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+)', "%Y-%m-%dT%H:%M:%S.%f"),
    # ISO 8601: 2024-01-15T13:45:22
    (r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})', "%Y-%m-%dT%H:%M:%S"),
    # Common log format: 2024-01-15 13:45:22,123
    (r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d+)', "%Y-%m-%d %H:%M:%S,%f"),
    # Common log format: 2024-01-15 13:45:22
    (r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', "%Y-%m-%d %H:%M:%S"),
    # Apache/nginx: 15/Jan/2024:13:45:22
    (r'(\d{2}/\w{3}/\d{4}:\d{2}:\d{2}:\d{2})', "%d/%b/%Y:%H:%M:%S"),
    # Syslog: Jan 15 13:45:22
    (r'(\w{3}\s+\d{1,2} \d{2}:\d{2}:\d{2})', "%b %d %H:%M:%S"),
]

_compiled = [(re.compile(pat), fmt) for pat, fmt in TIMESTAMP_PATTERNS]


def parse_timestamp(line: str) -> Optional[datetime]:
    """Extract and parse the first recognizable timestamp from a log line.

    Returns a datetime object or None if no timestamp is found.
    """
    for pattern, fmt in _compiled:
        match = pattern.search(line)
        if match:
            raw = match.group(1)
            try:
                dt = datetime.strptime(raw, fmt)
                # Syslog has no year — assume current year
                if dt.year == 1900:
                    dt = dt.replace(year=datetime.now().year)
                return dt
            except ValueError:
                continue
    return None


def parse_user_timestamp(value: str) -> datetime:
    """Parse a user-supplied timestamp string (flexible formats).

    Raises ValueError if the string cannot be parsed.
    """
    formats = [
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    raise ValueError(
        f"Cannot parse timestamp {value!r}. "
        "Expected formats like '2024-01-15 13:45:00' or '2024-01-15T13:45'."
    )
