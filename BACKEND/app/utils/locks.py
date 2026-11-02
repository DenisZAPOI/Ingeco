"""
One lock per key (a driver, a rider), kept in memory (audit F15).

A check then a write (the driver's timetable, then the acceptance) must not
be interleaved with the same check of another request. A conditional UPDATE
protects one row only; the check reads other rows.

In memory: valid for the MVP, which runs one process. With the MySQL
repositories, replace by `SELECT … FOR UPDATE` on the driver's (or the
rider's) row, inside the same transaction.
"""

import threading
from collections import defaultdict
from collections.abc import Iterator
from contextlib import contextmanager


class KeyedLock:
    def __init__(self) -> None:
        # One lock per account that ever used it: bounded by the number of accounts.
        self._locks: defaultdict[int, threading.Lock] = defaultdict(threading.Lock)
        self._guard = threading.Lock()

    @contextmanager
    def hold(self, key: int) -> Iterator[None]:
        with self._guard:
            lock = self._locks[key]
        with lock:
            yield
