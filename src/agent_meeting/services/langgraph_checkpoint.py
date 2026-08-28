from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager

from langgraph.checkpoint.sqlite import SqliteSaver


@contextmanager
def sqlite_checkpointer(path: str = "data/meetings.db") -> Iterator[SqliteSaver]:
    connection = sqlite3.connect(path, check_same_thread=False)
    saver = SqliteSaver(connection)
    saver.setup()
    try:
        yield saver
    finally:
        connection.close()
