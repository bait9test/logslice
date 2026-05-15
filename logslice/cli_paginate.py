"""CLI sub-command: paginate — page through a sliced log output."""

from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from logslice.paginator import paginate


def build_paginate_parser(
    parent: Optional[argparse._SubParsersAction] = None,
) -> argparse.ArgumentParser:
    """Build (and optionally register) the *paginate* argument parser."""
    kwargs = dict(
        description="Display a specific page of lines read from stdin or a file.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    if parent is not None:
        parser = parent.add_parser("paginate", **kwargs)
    else:
        parser = argparse.ArgumentParser(prog="logslice-paginate", **kwargs)

    parser.add_argument(
        "file",
        nargs="?",
        default="-",
        help="Input file (default: stdin).",
    )
    parser.add_argument(
        "-n", "--page-size",
        type=int,
        default=50,
        metavar="N",
        help="Lines per page.",
    )
    parser.add_argument(
        "-p", "--page",
        type=int,
        default=1,
        metavar="PAGE",
        help="1-based page number to display.",
    )
    parser.add_argument(
        "--info",
        action="store_true",
        help="Print page info header (page X of Y).",
    )
    return parser


def run_paginate(args: argparse.Namespace, out=sys.stdout, err=sys.stderr) -> int:
    """Execute the paginate command.  Returns an exit code."""
    try:
        if args.file == "-":
            raw_lines: List[str] = sys.stdin.readlines()
        else:
            with open(args.file, "r", encoding="utf-8", errors="replace") as fh:
                raw_lines = fh.readlines()
    except OSError as exc:
        err.write(f"error: {exc}\n")
        return 1

    try:
        page_lines, total_pages = paginate(
            [l.rstrip("\n") for l in raw_lines],
            page_size=args.page_size,
            page_number=args.page,
        )
    except ValueError as exc:
        err.write(f"error: {exc}\n")
        return 1

    if args.info:
        out.write(f"# page {args.page} of {total_pages}\n")

    for line in page_lines:
        out.write(line + "\n")

    return 0


def main() -> None:  # pragma: no cover
    parser = build_paginate_parser()
    sys.exit(run_paginate(parser.parse_args()))
