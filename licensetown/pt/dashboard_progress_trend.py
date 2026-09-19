"""Read-only 7-day Overall Progress history for the learner dashboard.

The current Overall Progress metric is state based (coverage / repair / retention),
so historical points are reconstructed from the same authoritative question
attempts rather than estimated from answer counts.  This module never writes
learner data and does not affect selection or Node-state persistence.
"""

from __future__ import annotations

from datetime import datetime, time, timedelta, timezone
from threading import Lock
from zoneinfo import ZoneInfo

from database import get_question_attempts
from field_evidence import build_field_evidence
from field_progress import build_field_progress


_TOKYO = ZoneInfo("Asia/Tokyo")
_CACHE: dict[tuple[str, int, str, str], list[dict]] = {}
_CACHE_LOCK = Lock()
_CACHE_MAX = 64


def _as_datetime(value) -> datetime | None:
    if isinstance(value, datetime):
        result = value
    elif isinstance(value, str) and value.strip():
        text = value.strip().replace("Z", "+00:00")
        try:
            result = datetime.fromisoformat(text)
        except ValueError:
            return None
    else:
        return None
    if result.tzinfo is None:
        result = result.replace(tzinfo=timezone.utc)
    return result


def _cache_key(user_id: str, attempts: list[dict], now_tokyo: datetime) -> tuple[str, int, str, str]:
    timestamps = [_as_datetime(item.get("answered_at")) for item in attempts]
    timestamps = [item for item in timestamps if item is not None]
    last = max(timestamps).isoformat() if timestamps else ""
    return (str(user_id), len(attempts), last, now_tokyo.date().isoformat())


def build_overall_progress_history_7d(
    attempts,
    *,
    now: datetime | None = None,
) -> list[dict]:
    """Reconstruct seven daily Overall Progress points from formal attempt history."""
    now_tokyo = (now or datetime.now(_TOKYO)).astimezone(_TOKYO)
    attempt_list = [dict(item) for item in (attempts or [])]
    timed_attempts: list[tuple[datetime, dict]] = []
    for item in attempt_list:
        answered_at = _as_datetime(item.get("answered_at"))
        if answered_at is not None:
            timed_attempts.append((answered_at.astimezone(_TOKYO), item))

    points: list[dict] = []
    for offset in range(6, -1, -1):
        day = now_tokyo.date() - timedelta(days=offset)
        if day == now_tokyo.date():
            as_of = now_tokyo
        else:
            as_of = datetime.combine(day, time.max, tzinfo=_TOKYO)
        eligible = [item for answered_at, item in timed_attempts if answered_at <= as_of]
        evidence = build_field_evidence(eligible, as_of=as_of)
        progress = build_field_progress(evidence)
        raw = float(progress["overall"]["overall_progress_score"] or 0.0)
        points.append({
            "date": day.isoformat(),
            "label": f"{day.month}/{day.day}",
            "progress": round(raw * 100, 1),
        })
    return points


def _history_for_user(user_id: str) -> list[dict]:
    attempts = get_question_attempts(user_id)
    now_tokyo = datetime.now(_TOKYO)
    key = _cache_key(user_id, attempts, now_tokyo)
    with _CACHE_LOCK:
        cached = _CACHE.get(key)
        if cached is not None:
            return [dict(item) for item in cached]
    history = build_overall_progress_history_7d(attempts, now=now_tokyo)
    with _CACHE_LOCK:
        if len(_CACHE) >= _CACHE_MAX:
            _CACHE.clear()
        _CACHE[key] = [dict(item) for item in history]
    return history


def install_dashboard_progress_trend(legacy, goukaku_module) -> None:
    """Decorate the production dashboard read path with read-only trend points."""
    if getattr(goukaku_module, "_lt_progress_trend_installed", False):
        return
    original = goukaku_module.build_dashboard

    def build_dashboard(user_id=None, include_learner_navigation=False):
        dashboard = original(
            user_id,
            include_learner_navigation=include_learner_navigation,
        )
        dashboard.setdefault("overall_progress_history_7d", [])
        if user_id and dashboard.get("overall_progress_ui_enabled"):
            dashboard["overall_progress_history_7d"] = _history_for_user(user_id)
        return dashboard

    goukaku_module.build_dashboard = build_dashboard
    # app.py imported build_dashboard by value; keep that legacy reference aligned.
    legacy.build_dashboard = build_dashboard
    goukaku_module._lt_progress_trend_installed = True
