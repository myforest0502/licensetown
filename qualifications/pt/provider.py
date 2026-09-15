"""PT bank adapter used by learning_engine and adaptive selector.

The root question_bank module remains the authoritative loader.
See docs/QUALIFICATION_THREE_LAYER_AUDIT_V01.md for the retained path boundary."""

from __future__ import annotations

import question_bank


class PTQuestionBankProvider:
    """Expose the formal PT bank through the question-bank provider contract."""

    qualification_id: str = "pt"

    def question_ids(self) -> tuple[str, ...]:
        return question_bank.question_ids()

    def get_question(self, q_id: str) -> dict:
        return question_bank.get_question(q_id)

    def get_question_tag(self, q_id: str) -> dict:
        return question_bank.get_question_tag(q_id)

    def get_quiz_question(self, q_id: str) -> dict:
        return question_bank.get_quiz_question(q_id)
