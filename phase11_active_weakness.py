"""Pure Phase11 active-weakness facts scoped to the current formal repair cycle."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from typing import Any, Iterable

from knowledge_node_canonical import canonicalize_knowledge_node_id
from knowledge_node_repair_cycle import (
    current_evaluable_repair_cycle,
    current_repair_cycle,
)
from knowledge_node_weakness_evidence import (
    NO_WRONG_EVIDENCE,
    derive_repeated_weakness_evidence,
)


def build_active_repair_weakness(
    attempts: Iterable[dict[str, Any]],
    *,
    as_of: datetime | None = None,
) -> dict[str, dict[str, Any]]:
    """Return current-cycle weakness facts keyed by canonical Node.

    Unknown may keep a Node in an active repairing run, but confirmed weakness
    is derived only from evaluable non-unknown attempts in that current run.
    Completed historical repair cycles are excluded.
    """
    attempts = [dict(item) for item in attempts]
    user_ids = {str(item.get("user_id") or "") for item in attempts}
    if len(user_ids) > 1:
        raise ValueError("attempts must belong to one user")

    histories: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in attempts:
        node = canonicalize_knowledge_node_id(
            str(item.get("knowledge_node_id") or "")
        )
        if not node or not item.get("question_id"):
            continue
        histories[node].append(item)

    result: dict[str, dict[str, Any]] = {}
    for node, history in sorted(histories.items()):
        active_cycle = current_repair_cycle(history, as_of=as_of)
        if not active_cycle:
            continue
        evaluable_cycle = current_evaluable_repair_cycle(history, as_of=as_of)
        weakness_records = derive_repeated_weakness_evidence(evaluable_cycle)
        weakness = weakness_records[0] if weakness_records else None
        evaluable_wrong = [
            item for item in evaluable_cycle if item.get("is_correct") is False
        ]
        active_wrong_question_ids = sorted({
            str(item.get("question_id") or "")
            for item in evaluable_wrong
            if item.get("question_id")
        })
        active_confident_wrong_question_ids = sorted({
            str(item.get("question_id") or "")
            for item in evaluable_wrong
            if item.get("question_id") and item.get("confidence") == 1
        })
        result[node] = {
            "canonical_node_id": node,
            "active_repair_cycle_attempt_count": len(active_cycle),
            "active_unknown_attempt_count": sum(
                item.get("answer_status") == "unknown" for item in active_cycle
            ),
            "active_evaluable_attempt_count": len(evaluable_cycle),
            "active_evaluable_wrong_attempt_count": len(evaluable_wrong),
            "active_evaluable_wrong_question_count": len(active_wrong_question_ids),
            "active_evaluable_wrong_question_ids": active_wrong_question_ids,
            "active_confident_wrong_count": sum(
                item.get("confidence") == 1 for item in evaluable_wrong
            ),
            "active_confident_wrong_question_ids": active_confident_wrong_question_ids,
            "active_has_confident_wrong": bool(active_confident_wrong_question_ids),
            "active_weakness_evidence_level": (
                weakness.get("evidence_level") if weakness else NO_WRONG_EVIDENCE
            ),
            "active_weakness_evidence_reason": (
                weakness.get("evidence_reason")
                if weakness else "No evaluable wrong answer exists in the current repair cycle."
            ),
        }
    return result
