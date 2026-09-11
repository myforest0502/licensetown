"""PT adapter for the existing learner-history persistence API.

This adapter preserves current PT behavior exactly. It does not add database
columns, change queries, or make Takken share PT history.
"""

from __future__ import annotations

from datetime import datetime

import database

from .config import PT


class PTLearningHistoryStore:
    """Expose the legacy PT learning-history API behind a qualification boundary."""

    qualification_id: str = PT.qualification_id

    def get_question_attempts(
        self, user_id: str, start_at: datetime | None = None
    ) -> list[dict]:
        return database.get_question_attempts(user_id, start_at=start_at)

    def get_question_history(self, user_id: str) -> list[dict]:
        return database.get_question_history(user_id)

    def is_initial_assessment_completed(self, user_id: str) -> bool:
        return database.is_initial_assessment_completed(user_id)

    def mark_initial_assessment_completed(self, user_id: str) -> None:
        database.mark_initial_assessment_completed(user_id)
