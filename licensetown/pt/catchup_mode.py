"""Catch-up mode for the PT learner dashboard.

The existing strict Knowledge Node finish score and dated pace curve remain the
single progress authority. This module NEVER changes formal answers or mastery.
"""
from __future__ import annotations

import math
from datetime import date
from typing import Any

PACE_ANCHORS = (
    (365, 0.0), (240, 2.0), (180, 5.0), (150, 15.0),
    (120, 30.0), (90, 50.0), (60, 70.0),
    (30, 88.0), (14, 96.0), (0, 100.0),
)
ENTER_AT_LAG_DAYS = 10
GOAL_HORIZON_DAYS = 14


def progress_at_days(days: int | float | None) -> float | None:
    if days is None:
        return None
    days = float(days)
    if not math.isfinite(days):
        return None
    if days >= PACE_ANCHORS[0][0]:
        return PACE_ANCHORS[0][1]
    if days <= 0:
        return 100.0
    for (first_day, first_progress), (last_day, last_progress) in zip(
        PACE_ANCHORS, PACE_ANCHORS[1:]
    ):
        if last_day <= days <= first_day:
            t = (first_day - days) / (first_day - last_day)
            return first_progress + (last_progress - first_progress) * t
    return None


def equivalent_days(progress: float | None) -> float | None:
    if progress is None or not math.isfinite(float(progress)):
        return None
    p = max(0.0, min(100.0, float(progress)))
    if p <= PACE_ANCHORS[0][1]:
        return float(PACE_ANCHORS[0][0])
    if p >= 100:
        return 0.0
    for (first_day, first_progress), (last_day, last_progress) in zip(
        PACE_ANCHORS, PACE_ANCHORS[1:]
    ):
        if first_progress <= p <= last_progress:
            width = last_progress - first_progress
            t = (p - first_progress) / width if width else 0.0
            return first_day - (first_day - last_day) * t
    return None


def pace_lag(days_to_exam: int | None, finish_ratio: float | None) -> int | None:
    if days_to_exam is None or finish_ratio is None:
        return None
    days = equivalent_days(float(finish_ratio) * 100)
    if days is None:
        return None
    # JS Math.round(x) is floor(x + 0.5), not Python bankers rounding.
    return max(0, -math.floor(float(days_to_exam) - days + 0.5))


def daily_repair_goal(days_to_exam: int, finish_ratio: float, node_count: int) -> int:
    """A bounded workload suggestion, not a promise of day-zero recovery.

    Assumes a 'repairing -> repaired' +0.60 formal Node score as an optimistic
    unit of progress. Actual Qs may fail, be ineligible or require spaced proof.
    """
    horizon = min(GOAL_HORIZON_DAYS, max(1, int(days_to_exam)))
    target = progress_at_days(max(int(days_to_exam) - horizon, 0))
    now_percent = float(finish_ratio) * 100
    if not node_count or target is None:
        return 10
    needed_nodes = max(0, target - now_percent) * int(node_count) / 60.0
    per_day = max(10, math.ceil(needed_nodes / horizon / 10) * 10)
    return min(60, per_day)


def _latest_transition(user_id: str) -> str | None:
    """Read only two light-weight activity types, not thousands of attempts."""
    import database
    if database.database_is_available():
        with database.get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT mode FROM learning_events
                    WHERE user_id = %s AND qualification_id = 'pt'
                      AND mode IN ('catchup_started', 'catchup_recovered')
                    ORDER BY answered_at DESC, event_key DESC LIMIT 1
                    """,
                    (user_id,),
                )
                row = cur.fetchone()
                return str(row[0]) if row else None
    events = database.get_learning_events(user_id)
    matches = [row for row in events if row.get("mode") in {
        "catchup_started", "catchup_recovered"
    }]
    matches.sort(key=lambda row: str(row.get("answered_at") or ""))
    return str(matches[-1]["mode"]) if matches else None


def calculate_catchup_status(
    days_to_exam: int | None,
    overall: dict[str, Any] | None,
    *,
    was_active: bool = False,
) -> dict[str, Any]:
    if not overall or days_to_exam is None:
        return {"active": False, "lag_days": None, "daily_goal": 0, "pending_nodes": 0}
    finish = overall.get("progress_raw")
    if finish is None:
        return {"active": False, "lag_days": None, "daily_goal": 0, "pending_nodes": 0}
    lag = pace_lag(days_to_exam, float(finish))
    if lag is None:
        return {"active": False, "lag_days": None, "daily_goal": 0, "pending_nodes": 0}
    states = overall.get("state_counts") or {}
    pending = int(states.get("repairing", 0)) + int(states.get("recheck_due", 0))
    # A one-question beginner cannot safely be treated as 200 days behind.
    # The exclusive mode requires enough real learner evidence to evaluate pace.
    insufficient_evidence = (
        overall.get("answer_count") is not None
        and int(overall["answer_count"]) < 100
    )
    # Persistent catch-up runs through 9..1 days, and releases at 0 days.
    # Never hide the normal study routes when there is no repair work to serve.
    active = bool(
        not insufficient_evidence
        and (lag >= ENTER_AT_LAG_DAYS or (was_active and lag > 0))
        and pending > 0
    )
    node_count = int(overall.get("total_unique_canonical_nodes") or sum(
        int(value) for value in states.values()
    ))
    goal = daily_repair_goal(days_to_exam, float(finish), node_count) if active else 0
    return {
        "active": active, "lag_days": lag, "daily_goal": goal,
        "pending_nodes": pending, "finish_ratio": float(finish),
        "goal_is_estimate": True,
    }


def get_catchup_status(
    user_id: str,
    days_to_exam: int | None,
    overall: dict[str, Any] | None,
    *,
    record_transition: bool = False,
) -> dict[str, Any]:
    """Compute once with the existing formal dashboard progress, optionally persist.

    Fail-open on unavailable transition history: never trap a learner in a
    locked study UI without a reliable way to recover.
    """
    initial = calculate_catchup_status(days_to_exam, overall)
    lag = initial.get("lag_days")
    was_active = False
    if user_id and lag is not None and lag < ENTER_AT_LAG_DAYS:
        try:
            was_active = _latest_transition(user_id) == "catchup_started"
        except Exception:
            was_active = False
    status = calculate_catchup_status(days_to_exam, overall, was_active=was_active)
    if record_transition and user_id:
        event_type = (
            "catchup_started" if status["active"] and not was_active
            else "catchup_recovered" if lag == 0 and was_active
            else None
        )
        if event_type:
            try:
                from database import record_activity_event
                record_activity_event(user_id, event_type, {
                    "lag_days": lag, "goal": status["daily_goal"],
                })
            except Exception:
                # The dashboard must remain accessible if activity logging fails.
                pass
    return status
