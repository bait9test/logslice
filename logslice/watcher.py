"""File-rotation-aware watcher that stitches tail streams across rotations."""

from __future__ import annotations

import os
import time
from typing import Callable, Iterator, Optional

from logslice.tail import tail_file


def _inode(path: str) -> Optional[int]:
    try:
        return os.stat(path).st_ino
    except FileNotFoundError:
        return None


def watch_file(
    path: str,
    *,
    poll_interval: float = 0.5,
    rotation_check_interval: float = 2.0,
    line_parser: Optional[Callable[[str], Optional[object]]] = None,
    stop_after: Optional[int] = None,
) -> Iterator[str]:
    """Yield new log lines, transparently handling log rotation.

    When the inode of *path* changes (or the file disappears and reappears)
    the watcher re-opens the file from the beginning so no lines are skipped.
    """
    yielded = 0
    current_inode = _inode(path)
    last_rotation_check = time.monotonic()

    # Use tail_file for the initial stream
    tail_gen = tail_file(
        path,
        poll_interval=poll_interval,
        line_parser=line_parser,
        stop_after=stop_after,
    )

    for line in tail_gen:
        now = time.monotonic()
        if now - last_rotation_check >= rotation_check_interval:
            new_inode = _inode(path)
            if new_inode != current_inode:
                # File was rotated — restart tail from new file
                current_inode = new_inode
                tail_gen = tail_file(
                    path,
                    poll_interval=poll_interval,
                    line_parser=line_parser,
                    stop_after=(stop_after - yielded) if stop_after else None,
                )
            last_rotation_check = now

        yield line
        yielded += 1
        if stop_after is not None and yielded >= stop_after:
            return
