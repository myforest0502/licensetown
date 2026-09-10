"""Shared fail-closed guard for short-term same-evidence-question repeats."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Iterable

from knowledge_node_state_transition import derive_all_user_node_states
from question_bank import get_question_tag
from question_equivalence import (
    canonicalize_question_evidence_id,
    canonicalize_question_evidence_node,
)


def blocked_short_term_evidence_ids(
    attempts: Iterable[dict[str, Any]],
    *,
    as_of: datetime | None = None,
) -> set[str]:
    """Return attempted evidence IDs that have no formal retention check due."""
    replay = []
    evidence_node_by_id: dict[str, str] = {}
    for value in attempts or ():
        item = dict(value)
        question_id = str(item.get("question_id") or "")
        if not question_id:
            continue
        raw_node_id = item.get("knowledge_node_id")
        if not raw_node_id:
            raw_node_id = get_question_tag(question_id).get("knowledge_node_id")
        node_id = canonicalize_question_evidence_node(question_id, raw_node_id)
        evidence_id = canonicalize_question_evidence_id(question_id)
        if not node_id or not evidence_id:
            continue
        item.setdefault("user_id", "short-term-repeat-guard")
        item["knowledge_node_id"] = node_id
        item.setdefault("answered_at", item.get("timestamp") or item.get("attempted_at"))
        replay.append(item)
        evidence_node_by_id[evidence_id] = str(node_id)

    states = {
        str(item["canonical_node_id"]): str(item["state"])
        for item in derive_all_user_node_states(
            replay,
            as_of=as_of or datetime.now(timezone.utc),
        )
    }
    return {
        evidence_id
        for evidence_id, node_id in evidence_node_by_id.items()
        if states.get(node_id) != "recheck_due"
    }


def is_short_term_repeat_blocked(
    question_id: str,
    blocked_evidence_ids: Iterable[str],
) -> bool:
    """Check a raw Q ID against canonical exact-repeat evidence identities."""
    blocked = {str(value) for value in blocked_evidence_ids}
    return canonicalize_question_evidence_id(str(question_id)) in blocked
