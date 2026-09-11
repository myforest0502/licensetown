"""Shared contract for qualification-scoped learner history access.

This interface keeps qualification identity explicit and does not select another
qualification implicitly.
"""

from __future__ import annotations

from datetime import datetime
from typing import Protocol


class LearningHistoryStore(Protocol):
    """Qualification-scoped learner history and state boundary."""

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

    def reset_qualification_state(self, user_id: str) -> None:
        """Clear learning state for this qualification without deleting the account."""
