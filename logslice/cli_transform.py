"""CLI entry-point for the transform subcommand."""

from __future__ import annotations

import argparse
import re
import sys
from typing import List

from logslice.transformer import (
    LineTransformer,
    append_text,
    chain,
    prepend_text,
    replace_field,
    strip_ansi,
    transform_lines,
    uppercase_level,
)


def build_transform_parser(
    subparsers: "argparse._SubParsersAction | None" = None,
) -> argparse.ArgumentParser:
    kwargs = dict(
        description="Apply text transformations to each log line.",
    )
    if subparsers is not None:
        parser = subparsers.add_parser("transform", **kwargs)
    else:
        parser = argparse.ArgumentParser(prog="logslice-transform", **kwargs)

    parser.add_argument("file", nargs="?", help="Input log file (default: stdin)")
    parser.add_argument(
        "--uppercase-level",
        action="store_true",
        help="Uppercase level tokens (info → INFO, etc.)",
    )
    parser.add_argument(
        "--strip-ansi",
        action="store_true",
        help="Remove ANSI colour escape sequences.",
    )
    parser.add_argument(
        "--replace",
        metavar="PATTERN=REPLACEMENT",
        action="append",
        default=[],
        help="Regex substitution in PATTERN=REPLACEMENT form (repeatable).",
    )
    parser.add_argument(
        "--prepend",
        metavar="TEXT",
        default=None,
        help="Prepend TEXT to every line.",
    )
    parser.add_argument(
        "--append",
        metavar="TEXT",
        default=None,
        help="Append TEXT to every line (before trailing newline).",
    )
    return parser


def run_transform(args: argparse.Namespace, out=None) -> None:
    if out is None:
        out = sys.stdout

    transformers: List[LineTransformer] = []

    if args.uppercase_level:
        transformers.append(uppercase_level)
    if args.strip_ansi:
        transformers.append(strip_ansi)
    for spec in args.replace:
        if '=' not in spec:
            print(f"error: --replace value must be PATTERN=REPLACEMENT, got: {spec!r}", file=sys.stderr)
            sys.exit(1)
        pattern, replacement = spec.split('=', 1)
        transformers.append(replace_field(pattern, replacement))
    if args.prepend:
        transformers.append(prepend_text(args.prepend))
    if args.append:
        transformers.append(append_text(args.append))

    if not transformers:
        transformers.append(lambda line: line)  # identity

    src = open(args.file) if args.file else sys.stdin
    try:
        for line in transform_lines(src, *transformers):
            out.write(line)
    finally:
        if args.file:
            src.close()


def main() -> None:  # pragma: no cover
    parser = build_transform_parser()
    run_transform(parser.parse_args())


if __name__ == "__main__":  # pragma: no cover
    main()
