"""Pure Phase11 active-weakness facts scoped to the current formal repair cycle."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from typing import Any, Iterable

from question_equivalence import canonicalize_question_evidence_node
from knowledge_node_repair_cycle import current_repair_cycle
from knowledge_node_weakness_evidence import (
    NO_WRONG_EVIDENCE,
    derive_repeated_weakness_evidence,
)


def _attempt_time_value(item: dict[str, Any]) -> Any:
    return item.get("attempted_at") or item.get("answered_at")


def build_active_repair_weakness(
    attempts: Iterable[dict[str, Any]],
    *,
    as_of: datetime | None = None,
    node_states: Iterable[dict[str, Any]] | None = None,
) -> dict[str, dict[str, Any]]:
    """Return current-cycle weakness facts keyed by canonical Node.

    Unknown may keep a Node in an active repairing run, but confirmed weakness
    is derived only from evaluable non-unknown attempts in that current run.
    Completed historical repair cycles are excluded.
    """
    attempts = list(attempts)
    user_ids = {str(item.get("user_id") or "") for item in attempts}
    if len(user_ids) > 1:
        raise ValueError("attempts must belong to one user")

    histories: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in attempts:
        question_id = str(item.get("question_id") or "")
        node = canonicalize_question_evidence_node(
            question_id,
            str(item.get("knowledge_node_id") or ""),
        )
        if not node or not question_id:
            continue
        histories[str(node)].append(item)

    state_by_node = (
        {
            str(item.get("canonical_node_id") or ""): str(item.get("state") or "")
            for item in node_states
        }
        if node_states is not None
        else None
    )

    result: dict[str, dict[str, Any]] = {}
    for node, history in sorted(histories.items()):
        if state_by_node is not None and state_by_node.get(node) != "repairing":
            continue
        active_cycle = current_repair_cycle(history, as_of=as_of)
        if not active_cycle:
            continue
        # Reuse the exact active cycle already derived above. Calling
        # current_evaluable_repair_cycle(history) would rediscover the same
        # boundary a second time.
        evaluable_cycle = [
            item for item in active_cycle
            if item.get("answer_status") != "unknown"
        ]
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
        last_wrong_time = (
            _attempt_time_value(evaluable_wrong[-1]) if evaluable_wrong else None
        )
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
            "active_last_evaluable_wrong_at": last_wrong_time,
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
