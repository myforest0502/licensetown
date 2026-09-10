"""Pure ordering guard for predictable five-question answer patterns."""

from __future__ import annotations


def _answer_position(question):
    sets = question.get("accepted_answer_sets") or ()
    if len(sets) == 1 and len(sets[0]) == 1:
        value = str(sets[0][0]).upper()
        return value if value in "ABCDE" else None
    value = str(question.get("answer") or "").upper()
    return value if len(value) == 1 and value in "ABCDE" else None


def has_predictable_answer_pattern(questions) -> bool:
    """Identify only conspicuous patterns, not ordinary random imbalance."""
    keys = [_answer_position(question) for question in questions]
    if len(keys) != 5 or any(key is None for key in keys):
        return False
    text = "".join(keys)
    if text in {"ABCDE", "EDCBA"} or len(set(keys)) == 1:
        return True
    if keys[0] == keys[2] == keys[4] and keys[1] == keys[3] and keys[0] != keys[1]:
        return True
    return any(keys[index] == keys[index + 1] == keys[index + 2] == keys[index + 3]
               for index in range(2))


def arrange_five_question_sets(questions, batch_size=5):
    """Reorder membership-preservingly when a five-item key pattern is obvious."""
    ordered = list(questions)
    if batch_size != 5:
        raise ValueError("answer-pattern guard requires five-question sets")
    for start in range(0, len(ordered), batch_size):
        end = min(start + batch_size, len(ordered))
        if end - start != batch_size or not has_predictable_answer_pattern(ordered[start:end]):
            continue
        repaired = False
        for left in range(start, end):
            for right in range(left + 1, len(ordered)):
                candidate = list(ordered)
                candidate[left], candidate[right] = candidate[right], candidate[left]
                if not has_predictable_answer_pattern(candidate[start:end]):
                    ordered = candidate
                    repaired = True
                    break
            if repaired:
                break
    return ordered
