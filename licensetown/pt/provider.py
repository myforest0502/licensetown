"""PT Question Bank adapter."""

from __future__ import annotations
import question_bank

class PTQuestionBankProvider:
    qualification_id: str = "pt"
    def question_ids(self) -> tuple[str, ...]:
        return question_bank.question_ids()
    def get_question(self, q_id: str) -> dict:
        return question_bank.get_question(q_id)
    def get_question_tag(self, q_id: str) -> dict:
        return question_bank.get_question_tag(q_id)
    def get_quiz_question(self, q_id: str) -> dict:
        return question_bank.get_quiz_question(q_id)
