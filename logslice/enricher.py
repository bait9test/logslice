"""Line enrichment: attach extra fields (host, env, run_id) to log lines."""
from __future__ import annotations

import re
import socket
from typing import Callable, Iterable, Iterator, Optional

# Matches an optional trailing newline so we can re-attach it cleanly.
_TRAIL = re.compile(r"(\n?)$")


def _inject(line: str, kv: str) -> str:
    """Insert *kv* (e.g. 'host=mybox') just before the trailing newline."""
    body = line.rstrip("\n")
    nl = "\n" if line.endswith("\n") else ""
    return f"{body} {kv}{nl}"


def enrich_host(lines: Iterable[str], hostname: Optional[str] = None) -> Iterator[str]:
    """Append ``host=<hostname>`` to every line."""
    host = hostname or socket.gethostname()
    tag = f"host={host}"
    for line in lines:
        yield _inject(line, tag)


def enrich_field(lines: Iterable[str], key: str, value: str) -> Iterator[str]:
    """Append an arbitrary ``key=value`` pair to every line."""
    if not key:
        raise ValueError("key must not be empty")
    tag = f"{key}={value}"
    for line in lines:
        yield _inject(line, tag)


def enrich_with(lines: Iterable[str], fn: Callable[[str], str]) -> Iterator[str]:
    """Apply a user-supplied *fn(line) -> suffix* and append its result."""
    for line in lines:
        suffix = fn(line)
        if suffix:
            yield _inject(line, suffix)
        else:
            yield line


def enrich_pipeline(
    lines: Iterable[str],
    *enrichers: Callable[[Iterable[str]], Iterator[str]],
) -> Iterator[str]:
    """Chain multiple enricher callables in order."""
    result: Iterable[str] = lines
    for enricher in enrichers:
        result = enricher(result)
    return iter(result)
