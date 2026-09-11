"""PT adapter for qualification-scoped learner-history persistence.

Production schema carries ``qualification_id``. This adapter makes the PT
boundary explicit while preserving the legacy in-memory fallback used when no
DATABASE_URL is configured.
"""

from __future__ import annotations

import json
from datetime import datetime

import database

from .config import PT


class PTLearningHistoryStore:
    """Expose PT learner history without reading another qualification's rows."""

    qualification_id: str = PT.qualification_id

    def get_question_attempts(
        self, user_id: str, start_at: datetime | None = None
    ) -> list[dict]:
        if not database.database_is_available():
            return database.get_question_attempts(user_id, start_at=start_at)

        with database.get_db_connection() as conn:
            with conn.cursor() as cur:
                if start_at is None:
                    cur.execute(
                        """
                        SELECT event_key, user_id, question_id, knowledge_node_id,
                               mode, selected_answers, is_correct, confidence,
                               answered_at, attempt_position
                        FROM question_attempts
                        WHERE user_id = %s AND qualification_id = %s
                        ORDER BY answered_at, event_key, attempt_position
                        """,
                        (user_id, self.qualification_id),
                    )
                else:
                    cur.execute(
                        """
                        SELECT event_key, user_id, question_id, knowledge_node_id,
                               mode, selected_answers, is_correct, confidence,
                               answered_at, attempt_position
                        FROM question_attempts
                        WHERE user_id = %s AND qualification_id = %s
                          AND answered_at >= %s
                        ORDER BY answered_at, event_key, attempt_position
                        """,
                        (user_id, self.qualification_id, start_at),
                    )
                columns = (
                    "event_key", "user_id", "question_id", "knowledge_node_id",
                    "mode", "selected_answers", "is_correct", "confidence",
                    "answered_at", "attempt_position",
                )
                attempts = [dict(zip(columns, row)) for row in cur.fetchall()]

        for attempt in attempts:
            attempt["answer_status"] = (
                "unknown" if not attempt.get("selected_answers") else "answered"
            )
        return attempts

    def get_question_history(self, user_id: str) -> list[dict]:
        if not database.database_is_available():
            return database.get_question_history(user_id)

        with database.get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT question_results, answered_at
                    FROM learning_events
                    WHERE user_id = %s AND qualification_id = %s
                    ORDER BY answered_at, event_key
                    """,
                    (user_id, self.qualification_id),
                )
                rows = cur.fetchall()

        history = []
        for question_results, answered_at in rows:
            if isinstance(question_results, str):
                try:
                    question_results = json.loads(question_results)
                except json.JSONDecodeError:
                    continue
            if not isinstance(question_results, list):
                continue
            for result in question_results:
                if isinstance(result, dict) and result.get("question_id"):
                    history.append({**result, "timestamp": answered_at})
        return history

    def is_initial_assessment_completed(self, user_id: str) -> bool:
        if not database.database_is_available():
            return database.is_initial_assessment_completed(user_id)

        with database.get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT initial_assessment_completed
                    FROM qualification_user_state
                    WHERE user_id = %s AND qualification_id = %s
                    """,
                    (user_id, self.qualification_id),
                )
                row = cur.fetchone()
                if row is not None:
                    return bool(row[0])
                cur.execute(
                    """
                    SELECT EXISTS (
                        SELECT 1 FROM learning_events
                        WHERE user_id = %s AND qualification_id = %s
                          AND answered_count > 0
                    )
                    """,
                    (user_id, self.qualification_id),
                )
                evidence = cur.fetchone()
        return bool(evidence and evidence[0])

    def mark_initial_assessment_completed(self, user_id: str) -> None:
        if not database.database_is_available():
            database.mark_initial_assessment_completed(user_id)
            return

        with database.get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO qualification_user_state (
                        user_id, qualification_id,
                        initial_assessment_completed, updated_at
                    )
                    VALUES (%s, %s, TRUE, NOW())
                    ON CONFLICT (user_id, qualification_id) DO UPDATE SET
                        initial_assessment_completed = TRUE,
                        updated_at = NOW()
                    """,
                    (user_id, self.qualification_id),
                )
        # Keep the legacy PT profile flag in sync during the transition period.
        database.mark_initial_assessment_completed(user_id)

    def reset_qualification_state(self, user_id: str) -> None:
        """Clear PT learning state while preserving account/profile identity."""
        if not database.database_is_available():
            for event_key in [
                key for key, event in database._local_learning_events.items()
                if event.get("user_id") == user_id
            ]:
                database._local_learning_events.pop(event_key, None)
            database._local_learning_seconds.pop(user_id, None)
            database._local_learning_time_events[:] = [
                event for event in database._local_learning_time_events
                if event.get("user_id") != user_id
            ]
            database._local_question_attempts[:] = [
                attempt for attempt in database._local_question_attempts
                if attempt.get("user_id") != user_id
            ]
            for state_key in [
                key for key in database._local_user_node_states if key[0] == user_id
            ]:
                database._local_user_node_states.pop(state_key, None)
            database._local_initial_assessment_completed.discard(user_id)
            return

        qualified_tables = (
            "question_attempts",
            "user_node_state",
            "learning_events",
            "learning_time_events",
            "qualification_learning_time_totals",
            "qualification_user_state",
            "paused_quiz_sessions",
            "web_learning_sessions",
        )
        with database.get_db_connection() as conn:
            with conn.cursor() as cur:
                for table in qualified_tables:
                    cur.execute(
                        f"DELETE FROM {table} WHERE user_id = %s AND qualification_id = %s",
                        (user_id, self.qualification_id),
                    )
                # These legacy fields are PT-only compatibility state during the
                # migration; preserve the profile/name/mode and monitor access.
                cur.execute(
                    "DELETE FROM learning_time_totals WHERE user_id = %s",
                    (user_id,),
                )
                cur.execute(
                    """
                    UPDATE user_profiles
                    SET initial_assessment_completed = FALSE, updated_at = NOW()
                    WHERE user_id = %s
                    """,
                    (user_id,),
                )
