"""Pure classification of repeated weakness evidence for canonical Nodes."""

from __future__ import annotations

from collections import defaultdict
from typing import Any, Iterable

from knowledge_node_canonical import canonicalize_knowledge_node_id


NO_WRONG_EVIDENCE = "NO_WRONG_EVIDENCE"
SINGLE_WRONG = "SINGLE_WRONG"
REPEATED_SAME_QUESTION_WRONG = "REPEATED_SAME_QUESTION_WRONG"
CROSS_QUESTION_WRONG = "CROSS_QUESTION_WRONG"
CROSS_QUESTION_CONFIDENT_WRONG = "CROSS_QUESTION_CONFIDENT_WRONG"
MIXED_EVIDENCE = "MIXED_EVIDENCE"


def _sort_key(attempt: dict[str, Any]) -> tuple[str, str, int, int]:
    return (
        str(attempt.get("attempted_at") or attempt.get("answered_at") or ""),
        str(attempt.get("event_key") or ""),
        int(attempt.get("attempt_position") or 0),
        int(attempt.get("id") or 0),
    )


def _classify(history: list[dict[str, Any]]) -> tuple[str, str]:
    wrong = [item for item in history if item.get("is_correct") is False]
    correct = [item for item in history if item.get("is_correct") is True]
    wrong_questions = {str(item["question_id"]) for item in wrong}

    if not wrong:
        return NO_WRONG_EVIDENCE, "No wrong answer is recorded for this canonical Node."
    if len(wrong_questions) >= 2:
        if any(item.get("confidence") == 1 for item in wrong):
            return (
                CROSS_QUESTION_CONFIDENT_WRONG,
                "Different questions were answered incorrectly and include a confidence=1 wrong answer.",
            )
        return (
            CROSS_QUESTION_WRONG,
            "Different questions in the same canonical Node were answered incorrectly.",
        )
    if correct:
        return MIXED_EVIDENCE, "Correct and wrong answers coexist without two distinct wrong questions."
    if len(wrong) >= 2:
        return (
            REPEATED_SAME_QUESTION_WRONG,
            "The same question was answered incorrectly more than once; this is not cross-question evidence.",
        )
    return SINGLE_WRONG, "Only one wrong question is recorded; weakness is not confirmed."


def derive_repeated_weakness_evidence(
    attempts: Iterable[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Return anonymous user/canonical-Node evidence records.

    User identifiers are used only as internal grouping keys and never included
    in returned records. Histories are sorted before classification so callers
    may provide attempts in any order.
    """
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for source in attempts:
        item = dict(source)
        question_id = str(item.get("question_id") or "")
        raw_node_id = str(item.get("knowledge_node_id") or "")
        if not question_id or not raw_node_id:
            continue
        canonical = canonicalize_knowledge_node_id(raw_node_id)
        grouped[(str(item.get("user_id") or ""), canonical)].append(item)

    result: list[dict[str, Any]] = []
    for (_user_key, canonical), history in sorted(grouped.items()):
        ordered = sorted(history, key=_sort_key)
        question_ids = {str(item["question_id"]) for item in ordered}
        wrong = [item for item in ordered if item.get("is_correct") is False]
        correct = [item for item in ordered if item.get("is_correct") is True]
        level, reason = _classify(ordered)
        result.append({
            "canonical_node_id": canonical,
            "distinct_question_count": len(question_ids),
            "wrong_question_count": len({str(item["question_id"]) for item in wrong}),
            "correct_question_count": len({str(item["question_id"]) for item in correct}),
            "confident_wrong_count": sum(item.get("confidence") == 1 for item in wrong),
            "first_wrong_question_id": str(wrong[0]["question_id"]) if wrong else None,
            "last_wrong_question_id": str(wrong[-1]["question_id"]) if wrong else None,
            "evidence_level": level,
            "evidence_reason": reason,
        })
    return result
