"""CLI entry point for the merge subcommand."""

from __future__ import annotations

import argparse
import sys
from typing import List

from logslice.merger import merge_logs


def build_merge_parser(parent: argparse._SubParsersAction = None) -> argparse.ArgumentParser:  # type: ignore[type-arg]
    kwargs = dict(
        description="Merge multiple log files into a single time-ordered stream.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    if parent is not None:
        parser = parent.add_parser("merge", **kwargs)
    else:
        parser = argparse.ArgumentParser(prog="logslice-merge", **kwargs)

    parser.add_argument(
        "files",
        nargs="+",
        metavar="FILE",
        help="Two or more log files to merge.",
    )
    parser.add_argument(
        "--drop-unparseable",
        action="store_true",
        default=False,
        help="Discard lines with no recognisable timestamp.",
    )
    parser.add_argument(
        "-o",
        "--output",
        metavar="FILE",
        default=None,
        help="Write merged output to FILE instead of stdout.",
    )
    return parser


def run_merge(args: argparse.Namespace) -> None:
    handles = []
    try:
        streams = []
        for path in args.files:
            fh = open(path, "r", encoding="utf-8", errors="replace")
            handles.append(fh)
            streams.append(fh)

        out = open(args.output, "w", encoding="utf-8") if args.output else sys.stdout
        try:
            for line in merge_logs(streams, drop_unparseable=args.drop_unparseable):
                out.write(line if line.endswith("\n") else line + "\n")
        finally:
            if args.output:
                out.close()
    finally:
        for fh in handles:
            fh.close()


def main(argv: List[str] = None) -> None:  # type: ignore[assignment]
    parser = build_merge_parser()
    args = parser.parse_args(argv)
    run_merge(args)


if __name__ == "__main__":
    main()
