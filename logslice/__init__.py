"""logslice — fast time-bounded log file slicing."""

__version__ = "0.1.0"
__author__ = "logslice contributors"

from logslice.timestamp_parser import parse_timestamp, parse_user_timestamp

__all__ = ["parse_timestamp", "parse_user_timestamp"]
