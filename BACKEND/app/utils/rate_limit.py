"""
Limit on failed attempts (login, activation code), kept in memory.

Counted per key (a phone number, for instance) and not per IP address: several
users often share one network (association, mission locale), and blocking the
IP would lock them all out.

In memory: counters are lost when the API restarts, and are not shared between
several API processes. Enough for the MVP, which runs one process.
"""

import threading
import time
from collections import deque
from collections.abc import Callable


class AttemptLimiter:
    def __init__(self, max_failures: int, window_seconds: float, clock: Callable[[], float] = time.monotonic):
        self._max_failures = max_failures
        self._window_seconds = window_seconds
        self._clock = clock
        self._failures: dict[str, deque[float]] = {}
        # The API serves requests in several threads.
        self._lock = threading.Lock()

    def is_blocked(self, key: str) -> bool:
        with self._lock:
            return len(self._recent_failures(key)) >= self._max_failures

    def record_failure(self, key: str) -> None:
        with self._lock:
            self._recent_failures(key).append(self._clock())

    def reset(self, key: str) -> None:
        with self._lock:
            self._failures.pop(key, None)

    def clear(self) -> None:
        with self._lock:
            self._failures.clear()

    def _recent_failures(self, key: str) -> deque[float]:
        failures = self._failures.setdefault(key, deque())
        oldest_kept = self._clock() - self._window_seconds
        while failures and failures[0] <= oldest_kept:
            failures.popleft()
        return failures
