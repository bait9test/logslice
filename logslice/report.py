"""Combine formatter and stats to produce a final report."""

import json
import sys
from typing import Iterable, List, TextIO

from logslice.formatter import write_output, SUPPORTED_FORMATS, FORMAT_RAW
from logslice.stats import collect_stats, summarise


def run_report(
    lines: Iterable[str],
    fmt: str = FORMAT_RAW,
    show_stats: bool = False,
    stats_fmt: str = "text",
    out: TextIO = sys.stdout,
    stats_out: TextIO = sys.stderr,
) -> None:
    """
    Write formatted log output and optionally print statistics.

    :param lines:      Iterable of log lines to process.
    :param fmt:        Output format for log lines (raw/json/jsonl/csv).
    :param show_stats: Whether to emit statistics after output.
    :param stats_fmt:  How to render stats: 'text' or 'json'.
    :param out:        Stream to write formatted log lines to.
    :param stats_out:  Stream to write statistics to.
    """
    if not show_stats:
        write_output(lines, fmt=fmt, out=out)
        return

    # Buffer lines so we can pass them through both formatter and stats.
    buffered: List[str] = list(lines)
    write_output(iter(buffered), fmt=fmt, out=out)

    stats = collect_stats(iter(buffered))

    if stats_fmt == "json":
        stats_out.write(json.dumps(stats.as_dict(), indent=2) + "\n")
    else:
        stats_out.write(summarise(stats) + "\n")


def validate_format(fmt: str) -> str:
    """Raise ValueError if fmt is not supported, else return it."""
    if fmt not in SUPPORTED_FORMATS:
        raise ValueError(
            f"Unknown output format {fmt!r}. Supported: {', '.join(SUPPORTED_FORMATS)}"
        )
    return fmt
