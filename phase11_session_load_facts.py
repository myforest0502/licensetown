"""Read-only same-day session-load facts for Phase 11 diagnostics.

This module deliberately reports evidence only.  It does not decide whether a
learner should stop, change route, alter question counts, or override Safety,
repair, retention, coverage, or the Phase 10 selector.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Iterable
from zoneinfo import ZoneInfo


TOKYO = ZoneInfo("Asia/Tokyo")
DEFAULT_BLOCK_SIZE = 50


def _parse_time(value: Any) -> datetime | None:
    if isinstance(value, datetime):
        parsed = value
    elif value:
        try:
            parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        except ValueError:
            return None
    else:
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def _accuracy(correct: int, answered: int) -> float | None:
    return round(100.0 * correct / answered, 1) if answered else None


def _ordered_today(
    attempts: Iterable[dict[str, Any]], *, as_of: datetime
) -> list[dict[str, Any]]:
    today = as_of.astimezone(TOKYO).date()
    rows: list[tuple[datetime, int, int, dict[str, Any]]] = []
    for raw in attempts:
        item = dict(raw)
        answered_at = _parse_time(item.get("answered_at") or item.get("attempted_at"))
        if not answered_at or answered_at.astimezone(TOKYO).date() != today:
            continue
        rows.append((
            answered_at,
            int(item.get("attempt_position") or 0),
            int(item.get("id") or 0),
            item,
        ))
    rows.sort(key=lambda value: (value[0], value[1], value[2]))
    return [item for *_keys, item in rows]


def build_same_day_session_load_facts(
    attempts: Iterable[dict[str, Any]],
    *,
    as_of: datetime | None = None,
    block_size: int = DEFAULT_BLOCK_SIZE,
) -> dict[str, Any]:
    """Return same-day volume, repeat structure, and chronological accuracy facts.

    The result intentionally contains no learner-facing recommendation and no
    fatigue/overpractice verdict.  The chronological blocks are cumulative
    same-day blocks, not proof of one uninterrupted study session.  Generic
    repeat accuracy is also kept separate from repeats that follow a wrong
    answer so it cannot be mistaken for repair effectiveness.
    """
    if block_size <= 0:
        raise ValueError("block_size must be positive")
    as_of = as_of or datetime.now(timezone.utc)
    if as_of.tzinfo is None:
        as_of = as_of.replace(tzinfo=timezone.utc)

    today = _ordered_today(attempts, as_of=as_of)
    answered_times = [
        _parse_time(item.get("answered_at") or item.get("attempted_at"))
        for item in today
    ]
    answered_times = [value for value in answered_times if value is not None]
    inter_attempt_gaps = [
        round((current - previous).total_seconds() / 60.0, 1)
        for previous, current in zip(answered_times, answered_times[1:])
    ]
    largest_gaps = sorted(inter_attempt_gaps, reverse=True)[:3]
    study_span_minutes = (
        round((answered_times[-1] - answered_times[0]).total_seconds() / 60.0, 1)
        if len(answered_times) >= 2 else 0.0 if answered_times else None
    )

    seen_questions: set[str] = set()
    previous_result_by_question: dict[str, bool | None] = {}
    first_attempt_count = first_correct = 0
    repeat_attempt_count = repeat_correct = 0
    wrong_to_correct = wrong_to_wrong = 0
    correct_to_correct = correct_to_wrong = 0

    for item in today:
        question_id = str(item.get("question_id") or "").strip().upper()
        is_repeat = bool(question_id and question_id in seen_questions)
        is_evaluable = item.get("answer_status") != "unknown"
        current_result = item.get("is_correct") if is_evaluable else None
        is_correct = current_result is True
        if is_repeat:
            repeat_attempt_count += 1
            repeat_correct += int(is_correct)
            previous_result = previous_result_by_question.get(question_id)
            if previous_result is False and current_result is True:
                wrong_to_correct += 1
            elif previous_result is False and current_result is False:
                wrong_to_wrong += 1
            elif previous_result is True and current_result is True:
                correct_to_correct += 1
            elif previous_result is True and current_result is False:
                correct_to_wrong += 1
        else:
            first_attempt_count += 1
            first_correct += int(is_correct)
        if question_id:
            seen_questions.add(question_id)
            previous_result_by_question[question_id] = current_result

    repeat_after_wrong_count = wrong_to_correct + wrong_to_wrong
    repeat_after_correct_count = correct_to_correct + correct_to_wrong

    blocks: list[dict[str, Any]] = []
    for start in range(0, len(today), block_size):
        chunk = today[start : start + block_size]
        correct = sum(
            item.get("is_correct") is True and item.get("answer_status") != "unknown"
            for item in chunk
        )
        blocks.append({
            "block": start // block_size + 1,
            "from_attempt": start + 1,
            "to_attempt": start + len(chunk),
            "answered_count": len(chunk),
            "correct_count": int(correct),
            "accuracy_percent": _accuracy(int(correct), len(chunk)),
        })

    first_full = blocks[0] if blocks and blocks[0]["answered_count"] == block_size else None
    last_full = next(
        (block for block in reversed(blocks) if block["answered_count"] == block_size),
        None,
    )
    leading_to_trailing_delta = None
    if first_full and last_full and first_full is not last_full:
        leading_to_trailing_delta = round(
            float(last_full["accuracy_percent"]) - float(first_full["accuracy_percent"]), 1
        )

    correct_count = sum(
        item.get("is_correct") is True and item.get("answer_status") != "unknown"
        for item in today
    )
    return {
        "date_jst": as_of.astimezone(TOKYO).date().isoformat(),
        "answered_count": len(today),
        "correct_count": int(correct_count),
        "accuracy_percent": _accuracy(int(correct_count), len(today)),
        "unique_question_count": len(seen_questions),
        "first_attempt_count": first_attempt_count,
        "first_attempt_correct_count": first_correct,
        "first_attempt_accuracy_percent": _accuracy(first_correct, first_attempt_count),
        "repeat_attempt_count": repeat_attempt_count,
        "repeat_correct_count": repeat_correct,
        "repeat_accuracy_percent": _accuracy(repeat_correct, repeat_attempt_count),
        "repeat_share_percent": _accuracy(repeat_attempt_count, len(today)),
        "repeat_after_wrong_count": repeat_after_wrong_count,
        "wrong_to_correct_count": wrong_to_correct,
        "wrong_to_wrong_count": wrong_to_wrong,
        "repeat_after_wrong_accuracy_percent": _accuracy(
            wrong_to_correct, repeat_after_wrong_count
        ),
        "repeat_after_correct_count": repeat_after_correct_count,
        "correct_to_correct_count": correct_to_correct,
        "correct_to_wrong_count": correct_to_wrong,
        "repeat_after_correct_accuracy_percent": _accuracy(
            correct_to_correct, repeat_after_correct_count
        ),
        "first_answered_at_jst": (
            answered_times[0].astimezone(TOKYO).isoformat() if answered_times else None
        ),
        "last_answered_at_jst": (
            answered_times[-1].astimezone(TOKYO).isoformat() if answered_times else None
        ),
        "study_span_minutes": study_span_minutes,
        "largest_inter_attempt_gaps_minutes": largest_gaps,
        "max_inter_attempt_gap_minutes": largest_gaps[0] if largest_gaps else None,
        "block_size": block_size,
        "block_scope": "same_day_cumulative",
        "blocks": blocks,
        "leading_to_trailing_full_block_accuracy_delta_pp": leading_to_trailing_delta,
        "diagnostic_only": True,
        "policy_note": (
            "Same-day volume and late accuracy are observational evidence only; "
            "cumulative blocks may span long breaks and do not by themselves prove "
            "fatigue, one continuous session, or a reason to block learning. Generic "
            "repeat accuracy must not be treated as repair effectiveness without "
            "checking the prior answer state."
        ),
    }
