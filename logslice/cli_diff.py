"""CLI entry-point for the log-diff feature."""
from __future__ import annotations

import argparse
import sys
from typing import Sequence

from logslice.differ import diff_logs, diff_summary


def build_diff_parser(
    subparsers: "argparse._SubParsersAction | None" = None,
) -> argparse.ArgumentParser:
    kwargs: dict = dict(
        description="Show differences between two log files.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    if subparsers is not None:
        parser = subparsers.add_parser("diff", **kwargs)
    else:
        parser = argparse.ArgumentParser(**kwargs)

    parser.add_argument("left", help="First (left) log file")
    parser.add_argument("right", help="Second (right) log file")
    parser.add_argument(
        "--mode",
        choices=["left", "right", "common", "all"],
        default="all",
        help="Which lines to emit (default: all)",
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Print a count summary instead of lines",
    )
    parser.add_argument(
        "--no-tag",
        dest="no_tag",
        action="store_true",
        help="Omit the leading < / > / = tag",
    )
    return parser


def run_diff(args: argparse.Namespace, out=None) -> None:
    if out is None:
        out = sys.stdout

    with open(args.left) as lf, open(args.right) as rf:
        left_lines = lf.readlines()
        right_lines = rf.readlines()

    if args.summary:
        counts = diff_summary(iter(left_lines), iter(right_lines))
        out.write(f"left_only : {counts['left_only']}\n")
        out.write(f"right_only: {counts['right_only']}\n")
        out.write(f"common    : {counts['common']}\n")
        return

    for tag, line in diff_logs(iter(left_lines), iter(right_lines), mode=args.mode):
        if args.no_tag:
            out.write(line)
        else:
            out.write(f"{tag} {line}")


def main(argv: Sequence[str] | None = None) -> None:
    parser = build_diff_parser()
    args = parser.parse_args(argv)
    run_diff(args)


if __name__ == "__main__":  # pragma: no cover
    main()
