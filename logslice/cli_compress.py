"""CLI entry-point for compressing / decompressing log slices.

Usage examples::

    # compress a plain log file
    logslice-compress compress input.log -o output.log.gz

    # decompress back to stdout
    logslice-compress decompress output.log.gz
"""

from __future__ import annotations

import argparse
import sys

from logslice.compressor import compress_to_file, decompress_from_file


def build_compress_parser(
    parser: argparse.ArgumentParser | None = None,
) -> argparse.ArgumentParser:
    """Return (or populate) an ArgumentParser for the compress sub-commands."""
    if parser is None:
        parser = argparse.ArgumentParser(
            prog="logslice-compress",
            description="Compress or decompress log files.",
        )

    sub = parser.add_subparsers(dest="action", required=True)

    # -- compress sub-command -------------------------------------------------
    cp = sub.add_parser("compress", help="Compress a plain-text log file.")
    cp.add_argument("input", help="Path to the plain-text log file.")
    cp.add_argument("-o", "--output", required=True, help="Output .gz path.")
    cp.add_argument(
        "-l",
        "--level",
        type=int,
        default=6,
        choices=range(1, 10),
        metavar="1-9",
        help="gzip compression level (default: 6).",
    )

    # -- decompress sub-command -----------------------------------------------
    dp = sub.add_parser("decompress", help="Decompress a .gz log file to stdout.")
    dp.add_argument("input", help="Path to the .gz log file.")

    return parser


def run_compress(args: argparse.Namespace) -> int:
    """Execute the compress / decompress action described by *args*.

    Returns:
        Exit code (0 = success, non-zero = error).
    """
    if args.action == "compress":
        try:
            with open(args.input) as fh:
                lines = fh.readlines()
            count = compress_to_file(lines, args.output, level=args.level)
            print(f"Compressed {count} lines -> {args.output}", file=sys.stderr)
        except FileNotFoundError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        return 0

    if args.action == "decompress":
        try:
            for line in decompress_from_file(args.input):
                sys.stdout.write(line)
        except FileNotFoundError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        return 0

    print(f"error: unknown action '{args.action}'", file=sys.stderr)
    return 2


def main(argv: list[str] | None = None) -> None:  # pragma: no cover
    parser = build_compress_parser()
    args = parser.parse_args(argv)
    sys.exit(run_compress(args))


if __name__ == "__main__":  # pragma: no cover
    main()
