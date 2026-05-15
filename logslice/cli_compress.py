"""CLI entry-point for log compression / decompression."""
from __future__ import annotations

import argparse
import sys
from typing import Sequence

from logslice.compressor import (
    compress_to_file,
    decompress_from_file,
    compress_lines,
    decompress_lines,
)


def build_compress_parser(
    subparsers: "argparse._SubParsersAction | None" = None,
) -> argparse.ArgumentParser:
    kwargs: dict = dict(
        description="Compress or decompress log files using gzip.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    if subparsers is not None:
        parser = subparsers.add_parser("compress", **kwargs)
    else:
        parser = argparse.ArgumentParser(**kwargs)

    sub = parser.add_subparsers(dest="action", required=True)

    enc = sub.add_parser("encode", help="Compress a log file")
    enc.add_argument("input", help="Plain-text log file to compress")
    enc.add_argument("output", help="Destination .gz file")
    enc.add_argument(
        "--level",
        type=int,
        default=9,
        choices=range(1, 10),
        metavar="1-9",
        help="Compression level (default: 9)",
    )

    dec = sub.add_parser("decode", help="Decompress a .gz log file")
    dec.add_argument("input", help="Compressed .gz file")
    dec.add_argument(
        "output",
        nargs="?",
        default="-",
        help="Destination file (default: stdout)",
    )

    return parser


def run_compress(args: argparse.Namespace, out=None) -> None:
    if out is None:
        out = sys.stdout

    if args.action == "encode":
        with open(args.input) as fh:
            lines = fh.readlines()
        compress_to_file(lines, args.output, level=args.level)
        out.write(f"Compressed {args.input} -> {args.output}\n")

    elif args.action == "decode":
        lines = list(decompress_from_file(args.input))
        if args.output == "-":
            for line in lines:
                out.write(line)
        else:
            with open(args.output, "w") as fh:
                fh.writelines(lines)
            out.write(f"Decompressed {args.input} -> {args.output}\n")


def main(argv: Sequence[str] | None = None) -> None:
    parser = build_compress_parser()
    args = parser.parse_args(argv)
    run_compress(args)


if __name__ == "__main__":  # pragma: no cover
    main()
