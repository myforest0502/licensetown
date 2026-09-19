"""Daily result summary for dashboard recommendation sessions.

This keeps the supporter/learner card grounded in the questions actually
answered from 「今日のおすすめ学習」 instead of lifetime or unrelated daily totals.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import database


def build_today_recommendation_summary(
    user_id: str,
    *,
    now: datetime | None = None,
    connection=None,
    question_result_rows=None,
) -> dict[str, int]:
    current = now or datetime.now(timezone.utc)
    today = current.astimezone(ZoneInfo("Asia/Tokyo")).date()
    rows = (
        question_result_rows
        if question_result_rows is not None
        else database._get_question_result_rows(user_id, connection)
    )

    answered = 0
    correct = 0
    for question_results, answered_at in rows:
        timestamp = answered_at
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)
        if timestamp.astimezone(ZoneInfo("Asia/Tokyo")).date() != today:
            continue
        if isinstance(question_results, str):
            try:
                question_results = json.loads(question_results)
            except json.JSONDecodeError:
                continue
        if not isinstance(question_results, list):
            continue
        for result in question_results:
            if not isinstance(result, dict):
                continue
            if result.get("learning_source") != "dashboard_recommendation":
                continue
            answered += 1
            if result.get("is_correct") is True:
                correct += 1

    return {
        "recommendation_today_answered": answered,
        "recommendation_today_correct": correct,
        "recommendation_today_incorrect": max(answered - correct, 0),
    }
