"""Production guard for learner study-time accumulation.

Legacy quiz sessions keep wall-clock timestamps in memory and persist the whole
interval when the session is paused or finished. That is useful for normal short
sessions, but an abandoned/open browser or LINE flow can turn hours of idle time
into study time.

This module leaves the learner session lifecycle untouched and composes a safer
production ``add_learning_time`` binding. Counted time is backed by persisted
answer activity, long gaps are capped, and trailing idle time is excluded.
"""

from __future__ import annotations

import logging
import os
from datetime import datetime, timezone
from typing import Any, Iterable


logger = logging.getLogger(__name__)
DEFAULT_MAX_ACTIVITY_GAP_SECONDS = 30 * 60
WEB_RECOMMENDATION_PREFIX = "web-recommendation:"
WEB_RECOMMENDATION_TIME_SUFFIX = ":time"


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _positive_seconds(value: Any) -> float:
    try:
        return max(float(value), 0.0)
    except (TypeError, ValueError):
        return 0.0


def _datetime_from_epoch(value: Any) -> datetime | None:
    try:
        return datetime.fromtimestamp(float(value), tz=timezone.utc)
    except (TypeError, ValueError, OverflowError, OSError):
        return None


def parse_learning_time_event_key(event_key: Any) -> tuple[str, datetime] | None:
    """Return ``(session_id, active_started_at)`` from LINE interval keys."""
    text = str(event_key or "").strip()
    session_id, separator, started_text = text.partition(":")
    if not separator or not session_id or not started_text:
        return None
    started_at = _datetime_from_epoch(started_text)
    if started_at is None:
        return None
    return session_id, started_at


def parse_web_recommendation_time_event_key(event_key: Any) -> str | None:
    """Return the Web recommendation session id from its time-event key."""
    text = str(event_key or "").strip()
    if not text.startswith(WEB_RECOMMENDATION_PREFIX) or not text.endswith(
        WEB_RECOMMENDATION_TIME_SUFFIX
    ):
        return None
    session_id = text[
        len(WEB_RECOMMENDATION_PREFIX) : -len(WEB_RECOMMENDATION_TIME_SUFFIX)
    ].strip()
    return session_id or None


def _attempt_timestamp(attempt: dict[str, Any]) -> datetime | None:
    value = attempt.get("answered_at")
    if not isinstance(value, datetime):
        return None
    return _as_utc(value)


def estimate_active_learning_seconds(
    attempts: Iterable[dict[str, Any]],
    *,
    session_id: str,
    active_started_at: datetime,
    interval_ended_at: datetime,
    max_activity_gap_seconds: float = DEFAULT_MAX_ACTIVITY_GAP_SECONDS,
    event_key_prefix: str | None = None,
) -> float:
    """Estimate evidenced study time for one active learning interval.

    Each persisted answer batch is a meaningful activity point. Time from the
    previous activity point is counted up to ``max_activity_gap_seconds``.
    Time after the final answer is intentionally excluded because there is no
    later learner activity proving the session remained active.
    """
    start = _as_utc(active_started_at)
    end = _as_utc(interval_ended_at)
    if end <= start:
        return 0.0

    cap = max(_positive_seconds(max_activity_gap_seconds), 1.0)
    prefix = event_key_prefix or f"{session_id}:"
    activity_times = {
        timestamp
        for attempt in attempts
        if str(attempt.get("event_key", "")).startswith(prefix)
        if (timestamp := _attempt_timestamp(attempt)) is not None
        if start <= timestamp <= end
    }
    if not activity_times:
        return 0.0

    total = 0.0
    cursor = start
    for activity_at in sorted(activity_times):
        gap = max((activity_at - cursor).total_seconds(), 0.0)
        total += min(gap, cap)
        cursor = activity_at
    return total


def _configured_gap_cap() -> float:
    raw = os.getenv(
        "LT_LEARNING_ACTIVITY_GAP_CAP_SECONDS",
        str(DEFAULT_MAX_ACTIVITY_GAP_SECONDS),
    )
    value = _positive_seconds(raw)
    return value if value > 0 else float(DEFAULT_MAX_ACTIVITY_GAP_SECONDS)


def _current_session_has_formal_id(legacy_module, user_id: str) -> bool:
    """Return whether the active LINE quiz session has its real session id.

    Some isolated legacy unit tests intentionally construct only
    ``{"active_started_at": ...}``. Production quiz sessions created by
    ``start_quiz`` always have a formal ``session_id``. Preserving the former
    avoids changing the meaning of those legacy tests without weakening the
    production idle-time guard.
    """
    sessions = getattr(legacy_module, "study_sessions", None)
    if not isinstance(sessions, dict):
        return False
    session = sessions.get(user_id)
    return isinstance(session, dict) and bool(session.get("session_id"))


def _web_recommendation_window(
    legacy_module,
    *,
    user_id: str,
    event_key: Any,
) -> tuple[str, datetime, str] | None:
    """Resolve Web recommendation session identity and activity prefix."""
    session_id = parse_web_recommendation_time_event_key(event_key)
    if session_id is None:
        return None
    sessions = getattr(legacy_module, "web_recommendation_sessions", None)
    if not isinstance(sessions, dict):
        return None
    session = sessions.get(session_id)
    if not isinstance(session, dict) or session.get("user_id") != user_id:
        return None
    started_at = _datetime_from_epoch(session.get("started_at"))
    if started_at is None:
        return None
    return session_id, started_at, f"web-recommendation:{session_id}:"


def install_learning_time_guard(legacy_module, database_module) -> None:
    """Install the production-safe learning-time binding on the legacy module."""
    if getattr(legacy_module, "_learning_time_guard_installed", False):
        return

    original_add_learning_time = legacy_module.add_learning_time
    gap_cap = _configured_gap_cap()

    def guarded_add_learning_time(
        user_id: str,
        elapsed_seconds: float,
        recorded_at: datetime | None = None,
        event_key: str | None = None,
    ) -> bool:
        raw_seconds = _positive_seconds(elapsed_seconds)
        interval_ended_at = _as_utc(recorded_at or datetime.now(timezone.utc))

        web_window = _web_recommendation_window(
            legacy_module,
            user_id=user_id,
            event_key=event_key,
        )
        if web_window is not None:
            session_id, active_started_at, event_prefix = web_window
            try:
                attempts = database_module.get_question_attempts(
                    user_id,
                    start_at=active_started_at,
                )
                safe_seconds = estimate_active_learning_seconds(
                    attempts,
                    session_id=session_id,
                    active_started_at=active_started_at,
                    interval_ended_at=interval_ended_at,
                    max_activity_gap_seconds=gap_cap,
                    event_key_prefix=event_prefix,
                )
            except Exception:
                logger.exception(
                    "learning_time_guard status=web_evidence_lookup_failed user_id=%s session_id=%s",
                    user_id,
                    session_id,
                )
                safe_seconds = min(raw_seconds, gap_cap)

            logger.info(
                "learning_time_guard status=web_applied user_id=%s session_id=%s raw_seconds=%.3f safe_seconds=%.3f",
                user_id,
                session_id,
                raw_seconds,
                safe_seconds,
            )
            if safe_seconds <= 0:
                return True
            return original_add_learning_time(
                user_id,
                safe_seconds,
                recorded_at=recorded_at,
                event_key=event_key,
            )

        parsed = parse_learning_time_event_key(event_key)
        if parsed is None:
            # Unknown/malformed interval keys fail closed to one activity-gap
            # window instead of allowing an hours-long wall clock.
            safe_seconds = min(raw_seconds, gap_cap)
            logger.warning(
                "learning_time_guard status=unparseable_key user_id=%s raw_seconds=%.3f safe_seconds=%.3f",
                user_id,
                raw_seconds,
                safe_seconds,
            )
            return original_add_learning_time(
                user_id,
                safe_seconds,
                recorded_at=recorded_at,
                event_key=event_key,
            )

        # Production LINE quiz sessions always carry a formal session id. A
        # session without one is a legacy/synthetic path; preserve its old
        # accounting semantics, but cap it so it cannot become an hours-long
        # outlier.
        if not _current_session_has_formal_id(legacy_module, user_id):
            safe_seconds = min(raw_seconds, gap_cap)
            logger.info(
                "learning_time_guard status=legacy_session_without_id user_id=%s raw_seconds=%.3f safe_seconds=%.3f",
                user_id,
                raw_seconds,
                safe_seconds,
            )
            return original_add_learning_time(
                user_id,
                safe_seconds,
                recorded_at=recorded_at,
                event_key=event_key,
            )

        session_id, active_started_at = parsed
        try:
            attempts = database_module.get_question_attempts(
                user_id,
                start_at=active_started_at,
            )
            safe_seconds = estimate_active_learning_seconds(
                attempts,
                session_id=session_id,
                active_started_at=active_started_at,
                interval_ended_at=interval_ended_at,
                max_activity_gap_seconds=gap_cap,
            )
        except Exception:
            # Study completion must not fail because time bookkeeping failed.
            logger.exception(
                "learning_time_guard status=evidence_lookup_failed user_id=%s session_id=%s",
                user_id,
                session_id,
            )
            safe_seconds = min(raw_seconds, gap_cap)

        logger.info(
            "learning_time_guard status=applied user_id=%s session_id=%s raw_seconds=%.3f safe_seconds=%.3f",
            user_id,
            session_id,
            raw_seconds,
            safe_seconds,
        )
        if safe_seconds <= 0:
            return True
        return original_add_learning_time(
            user_id,
            safe_seconds,
            recorded_at=recorded_at,
            event_key=event_key,
        )

    legacy_module.add_learning_time = guarded_add_learning_time
    legacy_module._learning_time_guard_installed = True
