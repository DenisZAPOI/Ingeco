"""
Limit on attempts (login, activation code, SMS codes…), kept in memory.

Counted per key: a phone number, an account, or a network address. Per number
first: several users often share one network (association, mission locale).
The limits per address are therefore much wider, only there to stop one
machine trying many numbers.

In memory: counters are lost when the API restarts, and are not shared between
several API processes. Enough for the MVP, which runs one process.
"""

import threading
import time
from collections import deque
from collections.abc import Callable

# Beyond this many keys, the next write drops those whose attempts are all
# older than the window: a stream of random numbers cannot fill the memory.
SWEEP_THRESHOLD = 10_000


class AttemptLimiter:
    def __init__(self, max_failures: int, window_seconds: float, clock: Callable[[], float] = time.monotonic):
        self._max_failures = max_failures
        self._window_seconds = window_seconds
        self._clock = clock
        self._failures: dict[str, deque[float]] = {}
        # The API serves requests in several threads.
        self._lock = threading.Lock()

    def try_record(self, key: str) -> bool:
        """Counts an attempt, unless the key is already blocked. False: blocked.

        Check and count in one step: parallel requests cannot all pass the
        check before any of them is counted.
        """
        with self._lock:
            failures = self._recent_failures(key)
            if len(failures) >= self._max_failures:
                return False
            self._add(key, failures)
            return True

    def cancel_last(self, key: str) -> None:
        """Takes back the last attempt counted: it turned out right."""
        with self._lock:
            failures = self._failures.get(key)
            if failures:
                failures.pop()
                if not failures:
                    del self._failures[key]

    def is_blocked(self, key: str) -> bool:
        with self._lock:
            return len(self._recent_failures(key)) >= self._max_failures

    def record_failure(self, key: str) -> None:
        with self._lock:
            self._add(key, self._recent_failures(key))

    def reset(self, key: str) -> None:
        with self._lock:
            self._failures.pop(key, None)

    def clear(self) -> None:
        with self._lock:
            self._failures.clear()

    def key_count(self) -> int:
        with self._lock:
            return len(self._failures)

    def _add(self, key: str, failures: deque[float]) -> None:
        if key not in self._failures and len(self._failures) >= SWEEP_THRESHOLD:
            self._sweep()
        failures.append(self._clock())
        self._failures[key] = failures

    def _sweep(self) -> None:
        for key in list(self._failures):
            # Drops the key once all its attempts are older than the window.
            self._recent_failures(key)

    def _recent_failures(self, key: str) -> deque[float]:
        """The attempts of `key` still inside the window. Creates nothing."""
        failures = self._failures.get(key, deque())
        oldest_kept = self._clock() - self._window_seconds
        while failures and failures[0] <= oldest_kept:
            failures.popleft()
        if not failures:
            self._failures.pop(key, None)
        return failures
