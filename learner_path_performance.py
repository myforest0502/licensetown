"""Privacy-safe, feature-gated timing for learner-facing request paths."""

from contextlib import contextmanager
from functools import wraps
import logging
import os
from time import perf_counter


logger = logging.getLogger(__name__)
_TRUE_VALUES = {"1", "true", "yes", "on"}


def enabled() -> bool:
    return os.getenv("LT_LEARNER_PATH_PERF_LOG", "").strip().lower() in _TRUE_VALUES


def _log(operation: str, duration_seconds: float, outcome: str = "ok") -> None:
    """Log only the fixed operation, elapsed time, and coarse outcome."""
    if not enabled():
        return
    try:
        logger.info(
            "lt_learner_path_perf op=%s duration_ms=%.3f outcome=%s",
            operation,
            max(duration_seconds, 0.0) * 1000.0,
            outcome,
        )
    except Exception:
        # Instrumentation must never affect the learner path.
        pass


@contextmanager
def measure(operation: str):
    if not enabled():
        yield
        return
    started_at = perf_counter()
    outcome = "ok"
    try:
        yield
    except BaseException:
        outcome = "error"
        raise
    finally:
        _log(operation, perf_counter() - started_at, outcome)


def timed(operation: str):
    """Measure a whole function without changing its return or exception behavior."""
    def decorator(function):
        @wraps(function)
        def wrapped(*args, **kwargs):
            with measure(operation):
                return function(*args, **kwargs)
        return wrapped
    return decorator
