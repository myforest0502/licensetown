"""Feature-gated timing for the learner-navigation start route.

Only operation names, durations, and response status are logged. Learner IDs,
tokens, questions, and answer content are deliberately outside this API.
"""

from contextlib import contextmanager
import logging
import os
from time import perf_counter


logger = logging.getLogger(__name__)
_TRUE_VALUES = {"1", "true", "yes", "on"}


def enabled() -> bool:
    return os.getenv("LT_LEARNER_NAVIGATION_PERF_LOG", "").strip().lower() in _TRUE_VALUES


class RequestTiming:
    def __init__(self):
        self.active = enabled()
        self.started_at = perf_counter() if self.active else None

    @contextmanager
    def measure(self, operation: str):
        if not self.active:
            yield
            return
        started_at = perf_counter()
        try:
            yield
        finally:
            self._log(operation, perf_counter() - started_at)

    def finish(self, status_code: int):
        if self.active and self.started_at is not None:
            self._log("route_total", perf_counter() - self.started_at, status=status_code)

    @staticmethod
    def _log(operation: str, duration_seconds: float, *, status=None):
        logger.info(
            "lt_learner_navigation_perf op=%s duration_ms=%.3f%s",
            operation,
            max(duration_seconds, 0.0) * 1000.0,
            f" status={status}" if status is not None else "",
        )
