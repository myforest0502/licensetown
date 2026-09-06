"""Read-only natural-use repair-effectiveness facts for Phase 11 QA.

These helpers summarize persisted adaptive selection outcomes only.  They do not
change Node state, selector behavior, repair ranking, Safety, or learner-facing
recommendations.  A correct STRONG alternate with confidence=1 is reported as a
formal-confirmation candidate, not independently promoted to a state change here.
"""

from __future__ import annotations

from datetime import datetime, timezone
import json
from typing import Any, Iterable
from zoneinfo import ZoneInfo


TOKYO = ZoneInfo("Asia/Tokyo")


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


def _results(event: dict[str, Any]) -> list[dict[str, Any]]:
    source = event.get("question_results")
    if isinstance(source, str):
        try:
            source = json.loads(source)
        except (TypeError, ValueError):
            return []
    if not isinstance(source, list):
        return []
    return [dict(item) for item in source if isinstance(item, dict)]


def build_same_day_repair_effectiveness_facts(
    learning_events: Iterable[dict[str, Any]],
    *,
    as_of: datetime | None = None,
) -> dict[str, Any]:
    """Summarize today's persisted adaptive repair attempts in JST."""
    as_of = as_of or datetime.now(timezone.utc)
    if as_of.tzinfo is None:
        as_of = as_of.replace(tzinfo=timezone.utc)
    today = as_of.astimezone(TOKYO).date()

    repair_results: list[dict[str, Any]] = []
    for event in learning_events or ():
        answered_at = _parse_time(event.get("answered_at"))
        if not answered_at or answered_at.astimezone(TOKYO).date() != today:
            continue
        for result in _results(event):
            if (
                result.get("learning_source") == "adaptive_daily"
                and result.get("selection_group") == "repair"
            ):
                repair_results.append(result)

    strong = [
        item for item in repair_results
        if item.get("repair_evidence_quality") == "different_question_strong"
    ]
    weak = [
        item for item in repair_results
        if item.get("repair_evidence_quality") == "different_question_weak"
    ]
    same = [
        item for item in repair_results
        if item.get("repair_evidence_quality") == "same_question"
    ]

    def is_correct(item: dict[str, Any]) -> bool:
        return item.get("is_correct") is True and item.get("answer_status") != "unknown"

    def confident_correct(item: dict[str, Any]) -> bool:
        return is_correct(item) and item.get("confidence") == 1

    def is_wrong(item: dict[str, Any]) -> bool:
        return item.get("is_correct") is False and item.get("answer_status") != "unknown"

    def distinct(items: list[dict[str, Any]], key: str) -> int:
        return len({str(item.get(key)) for item in items if item.get(key)})

    strong_correct = sum(is_correct(item) for item in strong)
    strong_confident_correct = sum(confident_correct(item) for item in strong)
    strong_wrong = sum(is_wrong(item) for item in strong)
    strong_confident_wrong = sum(
        is_wrong(item) and item.get("confidence") == 1 for item in strong
    )
    recent_repeat = sum(item.get("recent_question_repeat") is True for item in strong)
    cooldown_bypass = sum(item.get("recent_cooldown_bypassed") is True for item in strong)

    return {
        "date_jst": today.isoformat(),
        "adaptive_repair_attempt_count": len(repair_results),
        "strong_attempt_count": len(strong),
        "strong_correct_count": int(strong_correct),
        "strong_accuracy_percent": (
            round(100.0 * strong_correct / len(strong), 1) if strong else None
        ),
        "strong_confident_correct_count": int(strong_confident_correct),
        "strong_wrong_count": int(strong_wrong),
        "strong_confident_wrong_count": int(strong_confident_wrong),
        "strong_distinct_node_count": distinct(strong, "knowledge_node_id"),
        "strong_distinct_question_count": distinct(strong, "question_id"),
        "strong_recent_repeat_count": int(recent_repeat),
        "strong_cooldown_bypass_count": int(cooldown_bypass),
        "weak_attempt_count": len(weak),
        "weak_correct_count": sum(is_correct(item) for item in weak),
        "same_question_attempt_count": len(same),
        "same_question_correct_count": sum(is_correct(item) for item in same),
        "formal_confirmation_candidate_count": int(strong_confident_correct),
        "diagnostic_only": True,
        "policy_note": (
            "STRONG alternate outcomes are natural-use evidence only. A confident "
            "correct is a formal-confirmation candidate; durable repair still requires "
            "the normal Node-state and spaced-retention rules."
        ),
    }


def build_repair_effectiveness_evidence_line(facts: dict[str, Any] | None) -> str:
    """Serialize compact, non-identifying repair outcome facts for internal QA."""
    source = facts or {}

    def value(name: str) -> Any:
        result = source.get(name)
        return "none" if result is None else result

    return "repair_effectiveness=" + ",".join([
        f"date:{value('date_jst')}",
        f"adaptive_repair:{int(source.get('adaptive_repair_attempt_count') or 0)}",
        f"strong:{int(source.get('strong_attempt_count') or 0)}",
        f"strong_correct:{int(source.get('strong_correct_count') or 0)}",
        f"strong_accuracy:{value('strong_accuracy_percent')}",
        f"strong_confident_correct:{int(source.get('strong_confident_correct_count') or 0)}",
        f"strong_wrong:{int(source.get('strong_wrong_count') or 0)}",
        f"strong_nodes:{int(source.get('strong_distinct_node_count') or 0)}",
        f"strong_questions:{int(source.get('strong_distinct_question_count') or 0)}",
        f"recent_repeat:{int(source.get('strong_recent_repeat_count') or 0)}",
        f"cooldown_bypass:{int(source.get('strong_cooldown_bypass_count') or 0)}",
        f"weak:{int(source.get('weak_attempt_count') or 0)}",
        f"same_q:{int(source.get('same_question_attempt_count') or 0)}",
        f"formal_confirmation_candidates:{int(source.get('formal_confirmation_candidate_count') or 0)}",
    ])
