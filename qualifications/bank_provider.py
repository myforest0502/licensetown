"""Minimal qualification-scoped question-bank provider contract.

This module defines metadata/data access only. It is intentionally not wired
into the current PT runtime yet and must stay free of database/network effects.
"""

from __future__ import annotations

from typing import Protocol


class QuestionBankProvider(Protocol):
    """Smallest shared contract needed to read qualification question data."""

    qualification_id: str

    def question_ids(self) -> tuple[str, ...]:
        """Return stable question IDs in provider-defined order."""

    def get_question(self, q_id: str) -> dict:
        """Return the stored question record for one question ID."""

    def get_question_tag(self, q_id: str) -> dict:
        """Return qualification-specific learning metadata for one question."""

    def get_quiz_question(self, q_id: str) -> dict:
        """Return the learner-facing assembled quiz question."""
