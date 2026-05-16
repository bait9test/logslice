"""CLI entry-point for the log-enricher."""
from __future__ import annotations

import argparse
import sys
from functools import partial
from typing import List

from logslice.enricher import enrich_field, enrich_host, enrich_pipeline


def build_enrich_parser(
    subparsers=None,
) -> argparse.ArgumentParser:
    kwargs = dict(
        description="Append metadata fields to every log line.",
    )
    if subparsers is not None:
        parser = subparsers.add_parser("enrich", **kwargs)
    else:
        parser = argparse.ArgumentParser(prog="logslice-enrich", **kwargs)

    parser.add_argument("file", nargs="?", help="Input log file (default: stdin)")
    parser.add_argument(
        "--host",
        metavar="HOSTNAME",
        help="Append host=HOSTNAME to each line (uses system hostname if flag given without value)",
    )
    parser.add_argument(
        "--add-host",
        action="store_true",
        default=False,
        help="Append host=<system hostname> to each line",
    )
    parser.add_argument(
        "--field",
        metavar="KEY=VALUE",
        action="append",
        dest="fields",
        default=[],
        help="Append KEY=VALUE to each line (repeatable)",
    )
    return parser


def run_enrich(args: argparse.Namespace, out=None) -> None:
    if out is None:  # pragma: no cover
        out = sys.stdout

    src = open(args.file) if args.file else sys.stdin  # noqa: WPS515

    enrichers = []

    if args.add_host or args.host is not None:
        hostname = args.host if args.host else None
        enrichers.append(partial(enrich_host, hostname=hostname))

    for kv in args.fields:
        if "=" not in kv:
            raise SystemExit(f"--field value must be KEY=VALUE, got: {kv!r}")
        key, _, value = kv.partition("=")
        enrichers.append(partial(enrich_field, key=key, value=value))

    lines = enrich_pipeline(src, *enrichers)
    for line in lines:
        out.write(line if line.endswith("\n") else line + "\n")

    if args.file:
        src.close()


def main(argv: List[str] | None = None) -> None:  # pragma: no cover
    parser = build_enrich_parser()
    args = parser.parse_args(argv)
    run_enrich(args)


if __name__ == "__main__":  # pragma: no cover
    main()
