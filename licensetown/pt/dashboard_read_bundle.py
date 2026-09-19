"""Read bundle for the learner dashboard.

Production uses one Neon connection for dashboard aggregates, durable question
attempts, and Trial100 evidence. PT dashboard reads are explicitly
qualification-scoped during multi-qualification migration.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any
from zoneinfo import ZoneInfo

import database
from recommendation_daily_summary import build_today_recommendation_summary
from trial100_store import get_trial100_records


_QUALIFICATION_ID = "pt"
_ATTEMPT_COLUMNS = (
    "event_key",
    "user_id",
    "question_id",
    "knowledge_node_id",
    "mode",
    "selected_answers",
    "is_correct",
    "confidence",
    "answered_at",
    "attempt_position",
)


def _attempts_with_connection(user_id: str, connection) -> list[dict[str, Any]]:
    with connection.cursor() as cur:
        cur.execute(
            """
            SELECT event_key, user_id, question_id, knowledge_node_id,
                   mode, selected_answers, is_correct, confidence,
                   answered_at, attempt_position
            FROM question_attempts
            WHERE user_id = %s AND qualification_id = %s
            ORDER BY answered_at, event_key, attempt_position
            """,
            (user_id, _QUALIFICATION_ID),
        )
        attempts = [dict(zip(_ATTEMPT_COLUMNS, row)) for row in cur.fetchall()]
    for attempt in attempts:
        attempt["answer_status"] = (
            "unknown" if not attempt.get("selected_answers") else "answered"
        )
    return attempts


def _question_result_rows_with_connection(user_id: str, connection):
    """Return only PT learning-event question results on the shared connection."""
    with connection.cursor() as cur:
        cur.execute(
            """
            SELECT question_results, answered_at
            FROM learning_events
            WHERE user_id = %s
              AND qualification_id = %s
              AND question_results IS NOT NULL
            ORDER BY answered_at, event_key
            """,
            (user_id, _QUALIFICATION_ID),
        )
        return cur.fetchall()


def _summary_with_connection(
    user_id: str,
    connection,
    *,
    now: datetime | None = None,
) -> dict[str, int]:
    """Return the legacy summary shape using PT-only durable rows."""
    current = now or datetime.now(timezone.utc)
    today = current.astimezone(ZoneInfo("Asia/Tokyo")).date()
    seven_days_ago = current - timedelta(days=7)
    with connection.cursor() as cur:
        cur.execute(
            """
            SELECT
                COALESCE(SUM(answered_count), 0),
                COALESCE(SUM(correct_count), 0),
                COALESCE(SUM(answered_count) FILTER (WHERE answered_at >= %s), 0),
                COALESCE(SUM(correct_count) FILTER (WHERE answered_at >= %s), 0),
                COALESCE(SUM(answered_count) FILTER (
                    WHERE (answered_at AT TIME ZONE 'Asia/Tokyo')::date = %s
                ), 0)
            FROM learning_events
            WHERE user_id = %s AND qualification_id = %s
            """,
            (seven_days_ago, seven_days_ago, today, user_id, _QUALIFICATION_ID),
        )
        values = cur.fetchone()
        cur.execute(
            """
            SELECT COALESCE(total_seconds, 0)
            FROM qualification_learning_time_totals
            WHERE user_id = %s AND qualification_id = %s
            """,
            (user_id, _QUALIFICATION_ID),
        )
        row = cur.fetchone()
    return database._summary_values(*values, row[0] if row else 0)


def _activity_with_connection(
    user_id: str,
    connection,
    *,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Return the legacy seven-day activity shape using PT-only durable rows."""
    current = database._as_utc(now or datetime.now(timezone.utc))
    jst = ZoneInfo("Asia/Tokyo")
    today = current.astimezone(jst).date()
    dates = [today - timedelta(days=offset) for offset in range(6, -1, -1)]
    answers_by_date = {day: 0 for day in dates}
    correct_by_date = {day: 0 for day in dates}
    seconds_by_date = {day: 0.0 for day in dates}

    with connection.cursor() as cur:
        cur.execute(
            """
            SELECT answered_count, correct_count, answered_at
            FROM learning_events
            WHERE user_id = %s AND qualification_id = %s
            """,
            (user_id, _QUALIFICATION_ID),
        )
        learning_rows = cur.fetchall()
        cur.execute(
            """
            SELECT elapsed_seconds, recorded_at
            FROM learning_time_events
            WHERE user_id = %s AND qualification_id = %s
            """,
            (user_id, _QUALIFICATION_ID),
        )
        time_rows = cur.fetchall()

    active_dates = set()
    for answered_count, correct_count, answered_at in learning_rows:
        day = database._as_utc(answered_at).astimezone(jst).date()
        if int(answered_count) > 0:
            active_dates.add(day)
        if day in answers_by_date:
            answers_by_date[day] += int(answered_count)
            correct_by_date[day] += int(correct_count)
    for elapsed_seconds, recorded_at in time_rows:
        day = database._as_utc(recorded_at).astimezone(jst).date()
        if day in seconds_by_date:
            seconds_by_date[day] += float(elapsed_seconds)

    streak_days = database.calculate_learning_streak(active_dates, today)
    daily = [
        {
            "date": day.isoformat(),
            "label": f"{day.month}/{day.day}",
            "answered_count": answers_by_date[day],
            "correct_count": correct_by_date[day],
            "accuracy": (
                round(correct_by_date[day] / answers_by_date[day] * 100)
                if answers_by_date[day] else 0
            ),
            "study_minutes": round(seconds_by_date[day] / 60),
        }
        for day in dates
    ]
    weekly_minutes = round(sum(seconds_by_date.values()) / 60)
    weekly_answers = sum(answers_by_date.values())
    weekly_correct = sum(correct_by_date.values())
    return {
        "daily": daily,
        "streak_days": streak_days,
        "weekly_study_minutes": weekly_minutes,
        "average_daily_study_minutes": round(weekly_minutes / 7),
        "weekly_learning_days": sum(1 for value in answers_by_date.values() if value > 0),
        "weekly_answers": weekly_answers,
        "weekly_correct": weekly_correct,
        "weekly_accuracy": (
            round(weekly_correct / weekly_answers * 100) if weekly_answers else 0
        ),
    }


def get_learner_navigation_read_bundle(user_id: str) -> dict[str, Any]:
    """Return only the formal inputs needed to validate learner navigation.

    Production intentionally shares one connection for attempts and Trial100.
    Unlike the full dashboard bundle, this path does not calculate dashboard
    aggregates that cannot affect the structured CTA contract.
    """
    user_id = str(user_id or "").strip()
    if not user_id:
        return {"attempts": [], "trial100_records": []}
    if not database.database_is_available():
        return {
            "attempts": database.get_question_attempts(user_id),
            "trial100_records": get_trial100_records(user_id),
        }
    with database.get_db_connection() as conn:
        attempts = _attempts_with_connection(user_id, conn)
        trial100_records = get_trial100_records(user_id, connection=conn)
    return {
        "attempts": attempts,
        "trial100_records": trial100_records,
    }


def get_dashboard_read_bundle(
    user_id: str,
    *,
    include_attempts: bool = False,
    include_trial100: bool = False,
) -> dict[str, Any]:
    """Return dashboard facts and optional formal evidence with shared DB I/O."""
    user_id = str(user_id or "").strip()
    if not user_id:
        return {
            "learning_data": {
                "summary": {},
                "activity": {},
                "fields": [],
                "unique_question_count": 0,
            },
            "attempts": [],
            "trial100_records": [],
        }

    if not database.database_is_available():
        learning_data = database.get_dashboard_learning_data(user_id)
        learning_data.setdefault("activity", {}).update(
            build_today_recommendation_summary(user_id)
        )
        return {
            "learning_data": learning_data,
            "attempts": database.get_question_attempts(user_id) if include_attempts else [],
            "trial100_records": get_trial100_records(user_id) if include_trial100 else [],
        }

    with database.get_db_connection() as conn:
        question_rows = _question_result_rows_with_connection(user_id, conn)
        activity = _activity_with_connection(user_id, conn)
        activity.update(
            build_today_recommendation_summary(
                user_id,
                connection=conn,
                question_result_rows=question_rows,
            )
        )
        learning_data = {
            "summary": _summary_with_connection(user_id, conn),
            "activity": activity,
            "fields": database.get_field_learning_summary(
                user_id,
                _connection=conn,
                _question_result_rows=question_rows,
            ),
            "unique_question_count": database.get_unique_answered_question_count(
                user_id,
                _connection=conn,
                _question_result_rows=question_rows,
            ),
        }
        attempts = _attempts_with_connection(user_id, conn) if include_attempts else []
        trial100_records = (
            get_trial100_records(user_id, connection=conn) if include_trial100 else []
        )

    return {
        "learning_data": learning_data,
        "attempts": attempts,
        "trial100_records": trial100_records,
    }
