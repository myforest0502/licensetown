"""Shared fail-closed guard for short-term same-evidence-question repeats."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Iterable

from knowledge_node_state_transition import derive_all_user_node_states
from question_bank import get_question_tag
from question_equivalence import (
    canonicalize_question_evidence_id,
    canonicalize_question_evidence_node,
)


MIN_SAME_EVIDENCE_REPEAT_AFTER = timedelta(days=3)


def _as_datetime(value) -> datetime | None:
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None
    if not isinstance(value, datetime):
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def blocked_short_term_evidence_ids(
    attempts: Iterable[dict[str, Any]],
    *,
    as_of: datetime | None = None,
) -> set[str]:
    """Return attempted evidence IDs that are not safely eligible for replay.

    A Node becoming ``recheck_due`` may make an old evidence question eligible for
    a spaced retention check, but it must never reopen an evidence question that
    was itself attempted less than three real days ago.  This keeps the guard
    correct when one Node contains several evidence questions with different
    most-recent attempt times.
    """
    replay = []
    evidence_node_by_id: dict[str, str] = {}
    latest_attempt_by_evidence: dict[str, datetime] = {}
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

        attempted_at = _as_datetime(
            item.get("answered_at") or item.get("attempted_at") or item.get("timestamp")
        )
        if attempted_at is not None:
            previous = latest_attempt_by_evidence.get(evidence_id)
            if previous is None or attempted_at > previous:
                latest_attempt_by_evidence[evidence_id] = attempted_at

    effective_as_of = _as_datetime(as_of) or datetime.now(timezone.utc)
    states = {
        str(item["canonical_node_id"]): str(item["state"])
        for item in derive_all_user_node_states(
            replay,
            as_of=effective_as_of,
        )
    }

    blocked: set[str] = set()
    for evidence_id, node_id in evidence_node_by_id.items():
        if states.get(node_id) != "recheck_due":
            blocked.add(evidence_id)
            continue
        latest_attempt = latest_attempt_by_evidence.get(evidence_id)
        if latest_attempt is None:
            # Fail closed when timing evidence is unavailable.
            blocked.add(evidence_id)
            continue
        if effective_as_of - latest_attempt < MIN_SAME_EVIDENCE_REPEAT_AFTER:
            blocked.add(evidence_id)
    return blocked


def is_short_term_repeat_blocked(
    question_id: str,
    blocked_evidence_ids: Iterable[str],
) -> bool:
    """Check a raw Q ID against canonical exact-repeat evidence identities."""
    blocked = {str(value) for value in blocked_evidence_ids}
    return canonicalize_question_evidence_id(str(question_id)) in blocked
