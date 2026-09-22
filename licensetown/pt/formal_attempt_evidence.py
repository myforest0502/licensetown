"""Formal-evidence version boundary for the Q2234-Q2743 provisional rewrite.

Raw attempts remain durable history.  Attempts answered before the corrected
Q2234-Q2743 bank became live were made against different question wording and
must not be reused as evidence for the rewritten items.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Iterable

PROVISIONAL_REWRITE_FIRST_Q = 2234
PROVISIONAL_REWRITE_LAST_Q = 2743
PROVISIONAL_REWRITE_LIVE_AT = datetime(
    2026, 9, 22, 13, 48, 28, tzinfo=timezone.utc
)


def _as_utc(value: Any) -> datetime | None:
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


def _question_number(question_id: Any) -> int | None:
    text = str(question_id or "").upper()
    if not text.startswith("Q") or not text[1:].isdigit():
        return None
    return int(text[1:])


def is_current_formal_evidence(attempt: dict[str, Any]) -> bool:
    """Return whether an attempt is valid evidence for the current PT bank.

    Only the rewritten Q2234-Q2743 range has a version boundary.  Raw attempts
    are never deleted; this function is for derived learning-state input only.
    """
    number = _question_number(attempt.get("question_id"))
    if number is None:
        return True
    if not (PROVISIONAL_REWRITE_FIRST_Q <= number <= PROVISIONAL_REWRITE_LAST_Q):
        return True

    answered_at = _as_utc(
        attempt.get("answered_at")
        or attempt.get("attempted_at")
        or attempt.get("timestamp")
    )
    if answered_at is None:
        # Preserve historical compatibility when the timestamp is genuinely
        # unavailable; do not silently discard otherwise valid evidence.
        return True
    return answered_at >= PROVISIONAL_REWRITE_LIVE_AT


def filter_current_formal_evidence(
    attempts: Iterable[dict[str, Any]],
) -> list[dict[str, Any]]:
    return [dict(item) for item in attempts if is_current_formal_evidence(item)]
