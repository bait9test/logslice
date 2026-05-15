"""CLI entry-point for the log classifier."""

from __future__ import annotations

import argparse
import sys
from typing import Optional

from logslice.classifier import Rule, classify_lines, category_counts


def build_classify_parser(
    subparsers: Optional[argparse._SubParsersAction] = None,
) -> argparse.ArgumentParser:
    kwargs = dict(
        prog="logslice-classify",
        description="Classify log lines by pattern rules.",
    )
    if subparsers is not None:
        parser = subparsers.add_parser("classify", **kwargs)
    else:
        parser = argparse.ArgumentParser(**kwargs)

    parser.add_argument("file", help="Log file to classify (use - for stdin)")
    parser.add_argument(
        "-r",
        "--rule",
        action="append",
        metavar="NAME:PATTERN",
        dest="rules",
        default=[],
        help="Rule in NAME:PATTERN format; can be repeated.",
    )
    parser.add_argument(
        "--skip-unmatched",
        action="store_true",
        default=False,
        help="Suppress lines that match no rule.",
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        default=False,
        help="Print category counts to stderr after processing.",
    )
    return parser


def _parse_rules(raw: list[str]) -> list[Rule]:
    rules = []
    for item in raw:
        if ":" not in item:
            raise ValueError(f"Rule must be NAME:PATTERN, got: {item!r}")
        name, _, pattern = item.partition(":")
        rules.append(Rule.from_str(name.strip(), pattern.strip()))
    return rules


def run_classify(args: argparse.Namespace, out=None, err=None) -> None:
    out = out or sys.stdout
    err = err or sys.stderr

    rules = _parse_rules(args.rules)
    fh = sys.stdin if args.file == "-" else open(args.file)
    try:
        classified = list(
            classify_lines(fh, rules, skip_unmatched=args.skip_unmatched)
        )
    finally:
        if fh is not sys.stdin:
            fh.close()

    for item in classified:
        tag = f"[{item.category}] " if item.category else "[?] "
        line = item.line if item.line.endswith("\n") else item.line + "\n"
        out.write(tag + line)

    if args.stats:
        counts = category_counts(iter(classified))
        for cat, n in sorted(counts.items()):
            err.write(f"{cat}: {n}\n")


def main() -> None:
    parser = build_classify_parser()
    args = parser.parse_args()
    run_classify(args)


if __name__ == "__main__":
    main()
