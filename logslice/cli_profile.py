"""CLI entry-point for the log profiler."""

from __future__ import annotations

import argparse
import json
import sys

from logslice.profiler import profile_file


def build_profile_parser(subparsers=None) -> argparse.ArgumentParser:
    kwargs = dict(
        description="Profile a log file and print summary statistics."
    )
    if subparsers is not None:
        parser = subparsers.add_parser("profile", **kwargs)
    else:
        parser = argparse.ArgumentParser(prog="logslice-profile", **kwargs)

    parser.add_argument("file", help="Path to the log file to profile.")
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text).",
    )
    return parser


def run_profile(args: argparse.Namespace, out=None) -> None:
    if out is None:
        out = sys.stdout

    try:
        prof = profile_file(args.file)
    except FileNotFoundError:
        sys.stderr.write(f"error: file not found: {args.file}\n")
        sys.exit(1)

    if args.format == "json":
        data = {
            "total_lines": prof.total_lines,
            "total_bytes": prof.total_bytes,
            "first_timestamp": prof.first_timestamp.isoformat() if prof.first_timestamp else None,
            "last_timestamp": prof.last_timestamp.isoformat() if prof.last_timestamp else None,
            "duration_seconds": prof.duration.total_seconds() if prof.duration else None,
            "lines_per_second": prof.lines_per_second,
            "parse_errors": prof.parse_errors,
            "level_counts": prof.level_counts,
        }
        out.write(json.dumps(data, indent=2) + "\n")
    else:
        out.write(f"File            : {args.file}\n")
        out.write(f"Total lines     : {prof.total_lines}\n")
        out.write(f"Total bytes     : {prof.total_bytes}\n")
        out.write(f"First timestamp : {prof.first_timestamp}\n")
        out.write(f"Last timestamp  : {prof.last_timestamp}\n")
        out.write(f"Duration        : {prof.duration}\n")
        out.write(f"Lines/second    : {prof.lines_per_second}\n")
        out.write(f"Parse errors    : {prof.parse_errors}\n")
        if prof.level_counts:
            out.write(f"Level counts    : {prof.level_counts}\n")


def main() -> None:
    parser = build_profile_parser()
    args = parser.parse_args()
    run_profile(args)


if __name__ == "__main__":
    main()
