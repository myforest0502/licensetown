"""Qualification-explicit PT learning-event writer.

This writer is intentionally not installed into the live runtime yet. Production
activation requires the Phase-2a qualification-aware unique targets to exist
first. Keeping it dormant lets the SQL contract be reviewed and tested without
changing current PT behavior.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any
from zoneinfo import ZoneInfo

import database

from .config import PT


class PTLearningWriter:
    """Persist PT learning facts with qualification identity on every write."""

    qualification_id: str = PT.qualification_id

    def record_learning_batch(
        self,
        user_id: str,
        event_key: str,
        mode: str,
        answered_count: int,
        correct_count: int,
        answered_at: datetime | None = None,
        question_results: list[dict[str, Any]] | dict[str, Any] | None = None,
    ) -> bool:
        if not database.database_is_available():
            return database.record_learning_batch(
                user_id=user_id,
                event_key=event_key,
                mode=mode,
                answered_count=answered_count,
                correct_count=correct_count,
                answered_at=answered_at,
                question_results=question_results,
            )

        timestamp = answered_at or datetime.now(timezone.utc)
        attempts = database._result_attempts(question_results)
        encoded_results = (
            json.dumps(question_results, ensure_ascii=False)
            if question_results is not None
            else None
        )

        with database.get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO learning_events (
                        qualification_id, event_key, user_id, mode,
                        answered_count, correct_count, answered_at, question_results
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s::jsonb)
                    ON CONFLICT (qualification_id, event_key) DO NOTHING
                    """,
                    (
                        self.qualification_id,
                        event_key,
                        user_id,
                        mode,
                        answered_count,
                        correct_count,
                        timestamp,
                        encoded_results,
                    ),
                )
                if cur.rowcount != 1:
                    return False

                for attempt_position, result in attempts:
                    cur.execute(
                        """
                        INSERT INTO question_attempts (
                            qualification_id, event_key, user_id, question_id,
                            knowledge_node_id, mode, selected_answers, is_correct,
                            confidence, answered_at, attempt_position
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s::jsonb, %s, %s, %s, %s
                        )
                        """,
                        (
                            self.qualification_id,
                            event_key,
                            user_id,
                            result["question_id"],
                            result["knowledge_node_id"],
                            mode,
                            json.dumps(
                                result.get("selected_answers", []), ensure_ascii=False
                            ),
                            bool(result.get("is_correct")),
                            result.get("confidence"),
                            timestamp,
                            attempt_position,
                        ),
                    )

                    is_correct = bool(result.get("is_correct"))
                    confident_wrong = int(
                        not is_correct and result.get("confidence") == 1
                    )
                    cur.execute(
                        """
                        INSERT INTO user_node_state (
                            qualification_id, user_id, knowledge_node_id, state,
                            attempt_count, correct_count, incorrect_count,
                            confident_wrong_count, consecutive_correct,
                            first_seen_at, last_seen_at, last_correct_at,
                            last_incorrect_at, last_question_id, updated_at
                        ) VALUES (
                            %s, %s, %s, %s, 1, %s, %s, %s, %s, %s, %s,
                            %s, %s, %s, NOW()
                        )
                        ON CONFLICT (
                            qualification_id, user_id, knowledge_node_id
                        ) DO UPDATE SET
                            state = CASE
                                WHEN EXCLUDED.incorrect_count = 1 THEN 'repairing'
                                ELSE user_node_state.state
                            END,
                            attempt_count = user_node_state.attempt_count + 1,
                            correct_count = user_node_state.correct_count + EXCLUDED.correct_count,
                            incorrect_count = user_node_state.incorrect_count + EXCLUDED.incorrect_count,
                            confident_wrong_count = user_node_state.confident_wrong_count + EXCLUDED.confident_wrong_count,
                            consecutive_correct = CASE
                                WHEN EXCLUDED.incorrect_count = 1 THEN 0
                                ELSE user_node_state.consecutive_correct + 1
                            END,
                            last_seen_at = EXCLUDED.last_seen_at,
                            last_correct_at = COALESCE(
                                EXCLUDED.last_correct_at,
                                user_node_state.last_correct_at
                            ),
                            last_incorrect_at = COALESCE(
                                EXCLUDED.last_incorrect_at,
                                user_node_state.last_incorrect_at
                            ),
                            last_question_id = EXCLUDED.last_question_id,
                            updated_at = NOW()
                        """,
                        (
                            self.qualification_id,
                            user_id,
                            result["knowledge_node_id"],
                            "checking" if is_correct else "repairing",
                            int(is_correct),
                            int(not is_correct),
                            confident_wrong,
                            int(is_correct),
                            timestamp,
                            timestamp,
                            timestamp if is_correct else None,
                            timestamp if not is_correct else None,
                            result["question_id"],
                        ),
                    )
        return True

    def record_activity_event(
        self,
        user_id: str,
        activity_type: str,
        metadata: dict[str, Any] | None = None,
        occurred_at: datetime | None = None,
    ) -> bool:
        """Persist a PT non-answer activity using the same daily key contract."""
        timestamp = occurred_at or datetime.now(timezone.utc)
        jst_date = timestamp.astimezone(ZoneInfo("Asia/Tokyo")).date().isoformat()
        user_hash = hashlib.sha256(user_id.encode("utf-8")).hexdigest()[:16]
        activity_metadata = {"activity_type": activity_type}
        if metadata:
            activity_metadata.update(metadata)
        return self.record_learning_batch(
            user_id=user_id,
            event_key=f"{activity_type}:{user_hash}:{jst_date}",
            mode=activity_type,
            answered_count=0,
            correct_count=0,
            answered_at=timestamp,
            question_results=activity_metadata,
        )
