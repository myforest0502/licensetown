"""Privacy-first PostHog product analytics for LicenseTown.

Neon remains the source of truth for learning history.  This module records only
behavioral telemetry needed for product analysis.  Analytics must never block
the learner flow.
"""

from __future__ import annotations

import hashlib
import hmac
import logging
import os
import threading
from typing import Any, Mapping

logger = logging.getLogger(__name__)

_ALLOWED_PROPERTIES = {
    "analytics_environment",
    "surface",
    "mode",
    "learning_variant",
    "category_id",
    "question_id",
    "session_question_number",
    "session_question_count",
    "is_correct",
    "confidence",
    "response_time_ms",
    "batch_response_time_ms",
    "batch_size",
    "session_id",
    "current_set",
    "answered_count",
    "correct_count",
    "completion_reason",
    "floor_up_target_field",
    "source",
    "error_type",
    "endpoint",
    "http_status",
}

_client = None
_client_lock = threading.Lock()


def _enabled() -> bool:
    return bool(
        os.getenv("POSTHOG_PROJECT_API_KEY", "").strip()
        and os.getenv("POSTHOG_PSEUDONYM_SALT", "").strip()
    )


def analytics_environment() -> str:
    return os.getenv("LICENSETOWN_ANALYTICS_ENV", "development").strip() or "development"


def distinct_id_for_user(user_id: str | None) -> str | None:
    """Return a stable one-way pseudonym; never send the upstream user ID."""
    if not user_id:
        return None
    salt = os.getenv("POSTHOG_PSEUDONYM_SALT", "").encode("utf-8")
    if not salt:
        return None
    digest = hmac.new(salt, str(user_id).encode("utf-8"), hashlib.sha256).hexdigest()
    return "lt_" + digest[:32]


def learning_variant(session: Mapping[str, Any] | None) -> str:
    session = session or {}
    mode = str(session.get("mode") or "study")
    kind = str(session.get("session_kind") or "")
    if mode == "nekketsu":
        return "nekketsu"
    if kind == "adaptive_daily":
        return "bottom_up_lt" if session.get("floor_up_target_field") is not None else "normal_lt"
    if kind == "dashboard_recommendation":
        return "dashboard_recommendation"
    if kind == "initial_assessment":
        return "initial_assessment"
    if session.get("category_small") is not None:
        return "field_study"
    return kind or "random_lt"


def _posthog_client():
    global _client
    if not _enabled():
        return None
    if _client is not None:
        return _client
    with _client_lock:
        if _client is not None:
            return _client
        try:
            from posthog import Posthog
            _client = Posthog(
                os.environ["POSTHOG_PROJECT_API_KEY"],
                host=os.getenv("POSTHOG_HOST", "https://us.i.posthog.com"),
                debug=False,
                disable_geoip=True,
                flush_at=10,
                flush_interval=1.0,
                on_error=lambda error, items=None: logger.warning(
                    "PostHog upload failed: %s", type(error).__name__
                ),
            )
        except Exception:
            logger.exception("PostHog client initialization failed")
            _client = None
        return _client


def _safe_properties(properties: Mapping[str, Any] | None) -> dict[str, Any]:
    safe: dict[str, Any] = {
        "analytics_environment": analytics_environment(),
    }
    for key, value in dict(properties or {}).items():
        if key not in _ALLOWED_PROPERTIES or key == "analytics_environment":
            continue
        if value is None or isinstance(value, (str, int, float, bool)):
            safe[key] = value
    return safe


def capture(user_id: str | None, event: str, properties: Mapping[str, Any] | None = None) -> bool:
    """Best-effort capture.  Analytics failures are intentionally non-fatal."""
    distinct_id = distinct_id_for_user(user_id)
    client = _posthog_client()
    if not distinct_id or client is None:
        return False
    try:
        client.capture(
            event=str(event),
            distinct_id=distinct_id,
            properties=_safe_properties(properties),
        )
        return True
    except Exception:
        logger.exception("PostHog capture failed: event=%s", event)
        return False


def capture_with_distinct_id(
    distinct_id: str | None,
    event: str,
    properties: Mapping[str, Any] | None = None,
) -> bool:
    """Capture with an already-pseudonymized LicenseTown analytics ID."""
    if not distinct_id or not str(distinct_id).startswith("lt_"):
        return False
    client = _posthog_client()
    if client is None:
        return False
    try:
        client.capture(
            event=str(event),
            distinct_id=str(distinct_id),
            properties=_safe_properties(properties),
        )
        return True
    except Exception:
        logger.exception("PostHog capture failed: event=%s", event)
        return False


def flush(timeout: float = 2.0) -> None:
    """Best-effort flush for tests/controlled lifecycle points."""
    client = _client
    if client is None:
        return
    try:
        client.flush()
    except Exception:
        logger.exception("PostHog flush failed")
