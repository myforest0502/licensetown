"""Pure helper for the active formal repairing run of one canonical Node."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Iterable

from knowledge_node_state_transition import (
    derive_knowledge_node_state,
    derive_state_timeline,
)


def _sort_key(item: dict[str, Any]) -> tuple[str, str, int, int]:
    return (
        str(item.get("attempted_at") or item.get("answered_at") or ""),
        str(item.get("event_key") or ""),
        int(item.get("attempt_position") or 0),
        int(item.get("id") or 0),
    )


def current_repair_cycle(
    attempts: Iterable[dict[str, Any]],
    *,
    as_of: datetime | None = None,
) -> list[dict[str, Any]]:
    """Return attempts in the current consecutive formal repairing run.

    A completed repaired/stable cycle is not carried forward. If the current
    formal state is not repairing, there is no active repair cycle.
    """
    ordered = sorted((dict(item) for item in attempts), key=_sort_key)
    if not ordered:
        return []
    current = derive_knowledge_node_state(ordered, as_of=as_of)
    if current["state"] != "repairing":
        return []
    timeline = derive_state_timeline(ordered)
    if not timeline or timeline[-1]["state"] != "repairing":
        return []
    start = len(timeline) - 1
    while start > 0 and timeline[start - 1]["state"] == "repairing":
        start -= 1
    return ordered[start:]


def current_evaluable_repair_cycle(
    attempts: Iterable[dict[str, Any]],
    *,
    as_of: datetime | None = None,
) -> list[dict[str, Any]]:
    """Return only evaluable attempts from the active repair cycle."""
    return [
        item for item in current_repair_cycle(attempts, as_of=as_of)
        if item.get("answer_status") != "unknown"
    ]
