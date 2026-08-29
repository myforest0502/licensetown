"""Deterministic repair-confirmation strength for questions in one canonical Node."""

from question_bank import QuestionBankError, get_question_tag


SAME_QUESTION = "same_question"
DIFFERENT_QUESTION_WEAK = "different_question_weak"
DIFFERENT_QUESTION_STRONG = "different_question_strong"


def classify_repair_confirmation(previous_question_id: str, candidate_question_id: str) -> str:
    """Classify conservatively using existing reviewed metadata only.

    Different task or primary ability demonstrates a materially different demand.
    When metadata cannot prove that difference, fail closed as weak evidence.
    """
    previous = str(previous_question_id or "")
    candidate = str(candidate_question_id or "")
    if not previous or not candidate or previous == candidate:
        return SAME_QUESTION
    try:
        previous_tag = get_question_tag(previous)
        candidate_tag = get_question_tag(candidate)
    except (KeyError, ValueError, QuestionBankError):
        return DIFFERENT_QUESTION_WEAK
    previous_demand = (previous_tag.get("task"), previous_tag.get("primary_ability"))
    candidate_demand = (candidate_tag.get("task"), candidate_tag.get("primary_ability"))
    if all(previous_demand) and all(candidate_demand) and previous_demand != candidate_demand:
        return DIFFERENT_QUESTION_STRONG
    return DIFFERENT_QUESTION_WEAK
