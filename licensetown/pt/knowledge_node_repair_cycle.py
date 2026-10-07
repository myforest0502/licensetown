"""Pure helper for the active formal repairing run of one canonical Node."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Iterable

from knowledge_node_state_transition import _ordered_state_trace


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
    already_ordered: bool = False,
) -> list[dict[str, Any]]:
    """Return attempts in the current consecutive formal repairing run.

    A completed repaired/stable cycle is not carried forward. If the current
    formal state is not repairing, there is no active repair cycle.
    """
    # The active-cycle boundary depends on the state after each observed
    # attempt, not on the full evidence summary for every historical prefix.
    # _ordered_state_trace reproduces those exact states in one linear pass.
    ordered, states = _ordered_state_trace(
        attempts,
        already_ordered=already_ordered,
    )
    if not ordered or not states or states[-1] != "repairing":
        return []
    start = len(states) - 1
    while start > 0 and states[start - 1] == "repairing":
        start -= 1
    return ordered[start:]


def current_evaluable_repair_cycle(
    attempts: Iterable[dict[str, Any]],
    *,
    as_of: datetime | None = None,
    already_ordered: bool = False,
) -> list[dict[str, Any]]:
    """Return only evaluable attempts from the active repair cycle."""
    return [
        item for item in current_repair_cycle(
            attempts,
            as_of=as_of,
            already_ordered=already_ordered,
        )
        if item.get("answer_status") != "unknown"
    ]
