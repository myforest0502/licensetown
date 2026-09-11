"""Read bundle for the learner dashboard.

Production uses one Neon connection for dashboard aggregates, durable question
attempts, and Trial100 evidence. Formal PT evidence reads are qualification-
scoped during multi-qualification migration; summary/activity SQL remains on
its legacy path until its own small cutover.
"""

from __future__ import annotations

from typing import Any

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


def get_learner_navigation_read_bundle(user_id: str) -> dict[str, Any]:
    """Return only the formal inputs needed to validate learner navigation.

    Production intentionally shares one connection for attempts and Trial100.
    Unlike the full dashboard bundle, this path does not calculate legacy
    dashboard aggregates that cannot affect the structured CTA contract.
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
        activity = database.get_learning_activity(user_id, _connection=conn)
        activity.update(
            build_today_recommendation_summary(
                user_id,
                connection=conn,
                question_result_rows=question_rows,
            )
        )
        learning_data = {
            "summary": database.get_learning_summary(user_id, _connection=conn),
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
