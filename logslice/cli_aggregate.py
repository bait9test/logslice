"""CLI entry-point for the aggregate sub-command."""

from __future__ import annotations

import argparse
import json
import sys
from typing import List, Optional

from logslice.aggregator import aggregate, iter_buckets, top_buckets
from logslice.slicer import default_line_parser


def build_aggregate_parser(
    subparsers: Optional[argparse._SubParsersAction] = None,
) -> argparse.ArgumentParser:
    kwargs = dict(
        description="Count log lines grouped into fixed-width time buckets."
    )
    if subparsers is not None:
        parser = subparsers.add_parser("aggregate", **kwargs)
    else:
        parser = argparse.ArgumentParser(prog="logslice-aggregate", **kwargs)

    parser.add_argument("file", help="Path to log file (use - for stdin)")
    parser.add_argument(
        "--bucket",
        type=int,
        default=60,
        metavar="SECONDS",
        help="Bucket width in seconds (default: 60)",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=0,
        metavar="N",
        help="Show only the N busiest buckets (0 = show all)",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    return parser


def run_aggregate(args: argparse.Namespace, out=None) -> int:
    if out is None:
        out = sys.stdout

    try:
        fh = sys.stdin if args.file == "-" else open(args.file)
    except OSError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    try:
        lines = list(fh)
    finally:
        if fh is not sys.stdin:
            fh.close()

    try:
        counts = aggregate(lines, default_line_parser, bucket_seconds=args.bucket)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    pairs = top_buckets(counts, args.top) if args.top > 0 else list(iter_buckets(counts))

    if args.format == "json":
        json.dump(dict(pairs), out, indent=2)
        out.write("\n")
    else:
        for key, count in pairs:
            out.write(f"{key}  {count}\n")

    return 0


def main(argv: Optional[List[str]] = None) -> None:
    parser = build_aggregate_parser()
    args = parser.parse_args(argv)
    sys.exit(run_aggregate(args))


if __name__ == "__main__":
    main()
