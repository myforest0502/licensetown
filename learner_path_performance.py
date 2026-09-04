"""Privacy-safe, feature-gated timing for learner-facing request paths."""

from functools import wraps
import logging
import os
import sys
from time import perf_counter


logger = logging.getLogger(__name__)
_TRUE_VALUES = {"1", "true", "yes", "on"}
_SKIP_FALSE_RESULT_OPERATIONS = {"study_answer.total"}


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


class _Measurement:
    """Context manager that keeps timing passive even when exited manually."""

    def __init__(self, operation: str):
        self.operation = operation
        self.started_at = None

    def __enter__(self):
        if enabled():
            self.started_at = perf_counter()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.started_at is None:
            return False

        # Some legacy call sites manually pass (None, None, None) from a
        # finally block.  During exception propagation sys.exc_info() still
        # exposes the active exception, so preserve an accurate error outcome.
        active_exc_type = exc_type
        if active_exc_type is None:
            active_exc_type = sys.exc_info()[0]
        outcome = "error" if active_exc_type is not None else "ok"
        _log(self.operation, perf_counter() - self.started_at, outcome)
        return False


def measure(operation: str):
    return _Measurement(operation)


def timed(operation: str):
    """Measure a whole function without changing its return or exception behavior."""
    def decorator(function):
        @wraps(function)
        def wrapped(*args, **kwargs):
            if not enabled():
                return function(*args, **kwargs)

            started_at = perf_counter()
            try:
                result = function(*args, **kwargs)
            except BaseException:
                _log(operation, perf_counter() - started_at, "error")
                raise

            # process_study_answer_input is also used as a dispatcher probe.
            # False means this was not a real study-answer request, so do not
            # emit a misleading study_answer.total sample.
            if not (
                operation in _SKIP_FALSE_RESULT_OPERATIONS
                and result is False
            ):
                _log(operation, perf_counter() - started_at, "ok")
            return result

        return wrapped
    return decorator
