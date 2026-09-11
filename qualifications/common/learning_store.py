"""Shared contract for qualification-scoped learner history access.

This is an interface only. It does not change the existing database schema or
runtime storage behavior.
"""

from __future__ import annotations

from datetime import datetime
from typing import Protocol


class LearningHistoryStore(Protocol):
    """Small read/assessment-state boundary needed before storage is qualified."""

    qualification_id: str

    def get_question_attempts(
        self, user_id: str, start_at: datetime | None = None
    ) -> list[dict]:
        """Return formal per-question attempts for one qualification."""

    def get_question_history(self, user_id: str) -> list[dict]:
        """Return learner-facing question history for one qualification."""

    def is_initial_assessment_completed(self, user_id: str) -> bool:
        """Return whether this qualification's initial assessment is complete."""

    def mark_initial_assessment_completed(self, user_id: str) -> None:
        """Mark this qualification's initial assessment complete."""
