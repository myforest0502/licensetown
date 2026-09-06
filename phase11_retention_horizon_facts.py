"""Read-only upcoming-retention facts for Phase 11 diagnostics.

This module consumes formal Node-state output and reports when naturally repaired
Nodes are expected to become due. It never edits timestamps, promotes a Node,
or changes J1-J7 ordering or Phase10 selection.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Iterable
from zoneinfo import ZoneInfo


TOKYO = ZoneInfo("Asia/Tokyo")


def _as_datetime(value: Any) -> datetime | None:
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


def build_retention_horizon_facts(
    node_states: Iterable[dict[str, Any]],
    *,
    as_of: datetime | None = None,
) -> dict[str, Any]:
    """Summarize currently due and upcoming formal retention reviews."""
    as_of = _as_datetime(as_of) or datetime.now(timezone.utc)
    states = [dict(item) for item in node_states or ()]

    due_now = [item for item in states if item.get("state") == "recheck_due"]
    upcoming: list[tuple[datetime, dict[str, Any]]] = []
    for item in states:
        if item.get("state") not in {"repaired", "stable"}:
            continue
        next_review_at = _as_datetime(item.get("next_review_at"))
        if next_review_at and next_review_at > as_of:
            upcoming.append((next_review_at, item))
    upcoming.sort(key=lambda pair: (pair[0], str(pair[1].get("canonical_node_id") or "")))

    within_24h = sum(review_at <= as_of + timedelta(hours=24) for review_at, _ in upcoming)
    within_3d = sum(review_at <= as_of + timedelta(days=3) for review_at, _ in upcoming)
    within_7d = sum(review_at <= as_of + timedelta(days=7) for review_at, _ in upcoming)
    earliest = upcoming[0][0] if upcoming else None

    return {
        "as_of_jst": as_of.astimezone(TOKYO).isoformat(),
        "recheck_due_count": len(due_now),
        "upcoming_review_count": len(upcoming),
        "due_within_24h_count": int(within_24h),
        "due_within_3d_count": int(within_3d),
        "due_within_7d_count": int(within_7d),
        "earliest_review_at_jst": earliest.astimezone(TOKYO).isoformat() if earliest else None,
        "earliest_review_in_hours": (
            round((earliest - as_of).total_seconds() / 3600.0, 1) if earliest else None
        ),
        "diagnostic_only": True,
        "policy_note": (
            "Retention horizon is a forecast from formal Node state only. Do not "
            "alter learner timestamps or manufacture attempts to make a review due."
        ),
    }


def build_retention_horizon_evidence_line(facts: dict[str, Any] | None) -> str:
    """Serialize compact non-identifying retention timing facts."""
    source = facts or {}

    def value(name: str) -> Any:
        result = source.get(name)
        return "none" if result is None else result

    return "retention_horizon=" + ",".join([
        f"due_now:{int(source.get('recheck_due_count') or 0)}",
        f"upcoming:{int(source.get('upcoming_review_count') or 0)}",
        f"within_24h:{int(source.get('due_within_24h_count') or 0)}",
        f"within_3d:{int(source.get('due_within_3d_count') or 0)}",
        f"within_7d:{int(source.get('due_within_7d_count') or 0)}",
        f"earliest_at_jst:{value('earliest_review_at_jst')}",
        f"earliest_in_hours:{value('earliest_review_in_hours')}",
    ])
