"""CLI entry-point for the normalize sub-command."""

from __future__ import annotations

import argparse
import sys
from typing import Sequence

from logslice.normalizer import normalize_lines


def build_normalize_parser(
    parent: argparse._SubParsersAction | None = None,  # type: ignore[type-arg]
) -> argparse.ArgumentParser:
    kwargs: dict = dict(
        description="Normalize log lines: canonicalize level tokens and collapse whitespace.",
    )
    if parent is not None:
        parser: argparse.ArgumentParser = parent.add_parser("normalize", **kwargs)
    else:
        parser = argparse.ArgumentParser(prog="logslice-normalize", **kwargs)

    parser.add_argument("file", nargs="?", help="Log file to read (default: stdin)")
    parser.add_argument(
        "--no-level",
        dest="fix_level",
        action="store_false",
        default=True,
        help="Skip log-level canonicalization.",
    )
    parser.add_argument(
        "--no-whitespace",
        dest="fix_whitespace",
        action="store_false",
        default=True,
        help="Skip whitespace normalization.",
    )
    return parser


def run_normalize(args: argparse.Namespace, out=None) -> None:
    if out is None:  # pragma: no cover
        out = sys.stdout

    if args.file:
        fh = open(args.file, "r", encoding="utf-8", errors="replace")
    else:
        fh = sys.stdin

    try:
        for line in normalize_lines(
            fh,
            fix_level=args.fix_level,
            fix_whitespace=args.fix_whitespace,
        ):
            out.write(line)
            if not line.endswith("\n"):
                out.write("\n")
    finally:
        if args.file:
            fh.close()


def main(argv: Sequence[str] | None = None) -> None:  # pragma: no cover
    parser = build_normalize_parser()
    run_normalize(parser.parse_args(argv))


if __name__ == "__main__":  # pragma: no cover
    main()
