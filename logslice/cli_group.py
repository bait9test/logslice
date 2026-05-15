"""CLI entry-point for the grouper module."""
from __future__ import annotations

import argparse
import sys
from typing import List

from logslice.grouper import iter_groups, top_groups


def build_group_parser(subparsers=None) -> argparse.ArgumentParser:
    description = "Group log lines by a key field and display counts."
    if subparsers is not None:
        parser = subparsers.add_parser("group", help=description)
    else:
        parser = argparse.ArgumentParser(prog="logslice-group", description=description)

    parser.add_argument("file", nargs="?", help="Log file to read (default: stdin)")
    parser.add_argument(
        "--field",
        type=int,
        default=0,
        metavar="N",
        help="Zero-based whitespace-split field index to group by (default: 0)",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=0,
        metavar="N",
        help="Show only the top N groups by line count (0 = show all)",
    )
    parser.add_argument(
        "--counts-only",
        action="store_true",
        help="Print only '<count>\t<key>' instead of the grouped lines",
    )
    return parser


def run_group(args: argparse.Namespace, out=None) -> None:
    if out is None:
        out = sys.stdout

    field: int = args.field

    def key_fn(line: str) -> str:
        parts = line.split(None)
        if not parts:
            return ""
        return parts[field] if field < len(parts) else ""

    if args.file:
        fh = open(args.file, "r", encoding="utf-8", errors="replace")
    else:
        fh = sys.stdin

    try:
        lines: List[str] = fh.readlines()
    finally:
        if args.file:
            fh.close()

    if args.top and args.top > 0:
        pairs = top_groups(lines, n=args.top, key_fn=key_fn)
        for key, count in pairs:
            out.write(f"{count}\t{key}\n")
        return

    for key, group_lines in iter_groups(lines, key_fn=key_fn):
        if args.counts_only:
            out.write(f"{len(group_lines)}\t{key}\n")
        else:
            out.write(f"# {key} ({len(group_lines)} lines)\n")
            for ln in group_lines:
                out.write(ln if ln.endswith("\n") else ln + "\n")


def main() -> None:
    parser = build_group_parser()
    args = parser.parse_args()
    run_group(args)


if __name__ == "__main__":
    main()
