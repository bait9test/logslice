"""CLI entry-point for `logslice tail` — live log streaming."""

from __future__ import annotations

import argparse
import sys

from logslice.slicer import default_line_parser
from logslice.watcher import watch_file
from logslice.filters import pipeline, grep, filter_level


def build_tail_parser(parent: argparse._SubParsersAction) -> argparse.ArgumentParser:  # type: ignore[type-arg]
    p = parent.add_parser("tail", help="Stream new lines appended to a log file")
    p.add_argument("file", help="Log file to watch")
    p.add_argument("--grep", metavar="PATTERN", dest="grep_pattern",
                   help="Only show lines matching this regex")
    p.add_argument("--level", metavar="LEVEL",
                   help="Minimum log level (DEBUG/INFO/WARNING/ERROR/CRITICAL)")
    p.add_argument("--poll", type=float, default=0.25, metavar="SECS",
                   help="Polling interval in seconds (default: 0.25)")
    p.add_argument("--no-rotation", action="store_true",
                   help="Disable rotation detection (use plain tail)")
    return p


def run_tail(args: argparse.Namespace) -> int:
    filters = []
    if args.grep_pattern:
        filters.append(grep(args.grep_pattern))
    if args.level:
        filters.append(filter_level(args.level))

    stream = watch_file(
        args.file,
        poll_interval=args.poll,
        line_parser=default_line_parser,
    )

    lines = pipeline(stream, *filters) if filters else stream

    try:
        for line in lines:
            sys.stdout.write(line)
            sys.stdout.flush()
    except KeyboardInterrupt:
        pass
    return 0
