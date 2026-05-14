"""Command-line interface for logslice."""

import argparse
import sys
from datetime import datetime

from logslice.slicer import slice_log
from logslice.timestamp_parser import parse_user_timestamp


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="logslice",
        description="Extract a time-bounded slice from a log file.",
    )
    p.add_argument("file", help="Path to the log file")
    p.add_argument("start", help="Start timestamp (e.g. '2024-01-01 12:00:00')")
    p.add_argument("end", help="End timestamp (e.g. '2024-01-01 13:00:00')")
    p.add_argument(
        "--encoding",
        default="utf-8",
        help="File encoding (default: utf-8)",
    )
    p.add_argument(
        "--output",
        "-o",
        default=None,
        help="Write output to file instead of stdout",
    )
    return p


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        start_dt: datetime = parse_user_timestamp(args.start)
        end_dt: datetime = parse_user_timestamp(args.end)
    except ValueError as exc:
        print(f"error: invalid timestamp — {exc}", file=sys.stderr)
        return 1

    if start_dt > end_dt:
        print("error: start timestamp must not be after end timestamp", file=sys.stderr)
        return 1

    try:
        lines = slice_log(args.file, start_dt, end_dt, encoding=args.encoding)
        if args.output:
            with open(args.output, "w", encoding=args.encoding) as fh:
                for line in lines:
                    fh.write(line + "\n")
        else:
            for line in lines:
                print(line)
    except FileNotFoundError:
        print(f"error: file not found — {args.file}", file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
