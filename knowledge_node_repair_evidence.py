"""Deterministic repair-confirmation strength for questions in one canonical Node."""

import json
from pathlib import Path

from question_bank import QuestionBankError, get_question_tag


SAME_QUESTION = "same_question"
DIFFERENT_QUESTION_WEAK = "different_question_weak"
DIFFERENT_QUESTION_STRONG = "different_question_strong"
_FORMAL_PAIR_PATH = (
    Path(__file__).resolve().parent
    / "data"
    / "question_bank"
    / "strong_different_question_pairs.json"
)


def _load_formal_strong_pairs() -> frozenset[frozenset[str]]:
    try:
        records = json.loads(_FORMAL_PAIR_PATH.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError, TypeError):
        return frozenset()
    pairs = set()
    for record in records if isinstance(records, list) else ():
        question_ids = record.get("question_ids") if isinstance(record, dict) else None
        if (
            isinstance(question_ids, list)
            and len(question_ids) == 2
            and len(set(map(str, question_ids))) == 2
            and record.get("review_status") == "reviewed"
            and record.get("strength") == "strong"
        ):
            pairs.add(frozenset(map(str, question_ids)))
    return frozenset(pairs)


_FORMAL_STRONG_PAIRS = _load_formal_strong_pairs()


def classify_repair_confirmation(previous_question_id: str, candidate_question_id: str) -> str:
    """Classify conservatively using existing reviewed metadata only.

    Different task or primary ability demonstrates a materially different demand.
    When metadata cannot prove that difference, fail closed as weak evidence.
    """
    previous = str(previous_question_id or "")
    candidate = str(candidate_question_id or "")
    if not previous or not candidate or previous == candidate:
        return SAME_QUESTION
    if frozenset((previous, candidate)) in _FORMAL_STRONG_PAIRS:
        return DIFFERENT_QUESTION_STRONG
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
