"""Temporary, feature-gated timing probe for supporter first-open measurements.

No learner/supporter identifiers or payload content are logged. Enable only while
collecting Issue #100 baseline data with ``LT_SUPPORTER_PERF_LOG=1``.
"""

from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar
import logging
import os
from time import perf_counter
from uuid import uuid4


logger = logging.getLogger(__name__)
_TRACE_ID: ContextVar[str | None] = ContextVar("supporter_perf_trace_id", default=None)
_ROUTE_STARTED: ContextVar[float | None] = ContextVar("supporter_perf_route_started", default=None)
_TRUE_VALUES = {"1", "true", "yes", "on"}


def enabled() -> bool:
    return os.getenv("LT_SUPPORTER_PERF_LOG", "").strip().lower() in _TRUE_VALUES


def begin_request() -> str | None:
    if not enabled():
        return None
    trace_id = uuid4().hex[:12]
    _TRACE_ID.set(trace_id)
    _ROUTE_STARTED.set(perf_counter())
    return trace_id


def current_trace_id() -> str | None:
    return _TRACE_ID.get()


def log_duration(operation: str, duration_seconds: float, **facts) -> None:
    if not enabled():
        return
    safe_facts = " ".join(
        f"{key}={value}" for key, value in sorted(facts.items())
        if value is not None
    )
    logger.info(
        "lt_supporter_perf trace=%s op=%s duration_ms=%.3f%s",
        current_trace_id() or "none",
        operation,
        max(duration_seconds, 0.0) * 1000.0,
        f" {safe_facts}" if safe_facts else "",
    )


@contextmanager
def measure(operation: str):
    if not enabled():
        yield
        return
    started = perf_counter()
    try:
        yield
    finally:
        log_duration(operation, perf_counter() - started)


def finish_request(status_code: int | None = None) -> None:
    if not enabled():
        return
    started = _ROUTE_STARTED.get()
    if started is not None:
        log_duration("http_total", perf_counter() - started, status=status_code)
    _TRACE_ID.set(None)
    _ROUTE_STARTED.set(None)
