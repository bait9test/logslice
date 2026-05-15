"""CLI entry-point for the annotate sub-command."""
from __future__ import annotations

import argparse
import sys
from typing import Callable

from logslice.annotator import annotate_offset, annotate_sequence, annotate_tag


def build_annotate_parser(parent: argparse._SubParsersAction | None = None) -> argparse.ArgumentParser:  # noqa: SLF001
    description = "Annotate log lines with sequence numbers, byte offsets, or custom tags."
    if parent is not None:
        p = parent.add_parser("annotate", help=description, description=description)
    else:
        p = argparse.ArgumentParser(prog="logslice-annotate", description=description)

    p.add_argument("file", nargs="?", help="Input file (default: stdin).")
    mode = p.add_mutually_exclusive_group()
    mode.add_argument(
        "--sequence", "-n",
        action="store_true",
        default=True,
        help="Prepend sequence numbers (default).",
    )
    mode.add_argument(
        "--offset", "-b",
        action="store_true",
        help="Prepend byte offsets instead of sequence numbers.",
    )
    p.add_argument(
        "--start",
        type=int,
        default=1,
        metavar="N",
        help="Starting sequence number or byte offset (default: 1 / 0).",
    )
    p.add_argument(
        "--prefix",
        default="",
        help="String to place before the annotation value.",
    )
    p.add_argument(
        "--suffix",
        default=" ",
        help="String to place after the annotation value (default: single space).",
    )
    return p


def run_annotate(args: argparse.Namespace, out=None) -> None:  # pragma: no branch
    if out is None:
        out = sys.stdout

    fh = open(args.file) if args.file else sys.stdin  # noqa: WPS515
    try:
        lines = list(fh)
    finally:
        if args.file:
            fh.close()

    if args.offset:
        byte_start = max(args.start, 0)
        for offset, line in annotate_offset(lines, byte_start=byte_start):
            out.write(f"{args.prefix}{offset}{args.suffix}{line.rstrip(chr(10))}\n")
    else:
        start = args.start if args.start >= 1 else 1
        for line in annotate_sequence(lines, start=start, prefix=args.prefix, suffix=args.suffix):
            out.write(line)


def main() -> None:
    parser = build_annotate_parser()
    args = parser.parse_args()
    run_annotate(args)


if __name__ == "__main__":  # pragma: no cover
    main()
