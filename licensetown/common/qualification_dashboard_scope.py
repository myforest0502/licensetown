"""Qualification-scoped composition for dashboard side routes.

The main dashboard bundle is already explicitly PT-scoped in Production. This
module closes the remaining direct legacy reads used by footprints and the
supporter weekly-question page without changing their public route contracts.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from qualifications.common.learning_store_registry import get_learning_history_store


def _ordered_question_ids(values):
    def key(value):
        text = str(value)
        return (
            int(text[1:]) if text.startswith("Q") and text[1:].isdigit() else 10**9,
            text,
        )

    return sorted(values, key=key)


def _is_unknown_attempt(item):
    return (
        item.get("answer_status") == "unknown"
        or (not item.get("selected_answers") and item.get("confidence") is None)
    )


def build_pt_weekly_question_history(
    user_id: str,
    *,
    now: datetime | None = None,
    store=None,
):
    """Return the existing weekly-question shape from PT-only formal attempts."""
    history_store = store or get_learning_history_store("pt")
    jst = ZoneInfo("Asia/Tokyo")
    current = now or datetime.now(timezone.utc)
    if current.tzinfo is None:
        current = current.replace(tzinfo=timezone.utc)
    end_date = current.astimezone(jst).date()
    start_date = end_date - timedelta(days=6)
    start_at = datetime.combine(start_date, datetime.min.time(), jst).astimezone(timezone.utc)
    end_at = datetime.combine(
        end_date + timedelta(days=1), datetime.min.time(), jst
    ).astimezone(timezone.utc)

    attempts = [
        item
        for item in history_store.get_question_attempts(user_id, start_at=start_at)
        if item.get("answered_at") is not None
        and (
            item["answered_at"].replace(tzinfo=timezone.utc)
            if item["answered_at"].tzinfo is None
            else item["answered_at"].astimezone(timezone.utc)
        ) < end_at
    ]
    attempted = {str(item.get("question_id")) for item in attempts}
    wrong = {
        str(item.get("question_id"))
        for item in attempts
        if item.get("is_correct") is False and not _is_unknown_attempt(item)
    }
    unknown = {
        str(item.get("question_id"))
        for item in attempts
        if _is_unknown_attempt(item)
    }
    confident_wrong = {
        str(item.get("question_id"))
        for item in attempts
        if item.get("is_correct") is False
        and item.get("confidence") == 1
        and not _is_unknown_attempt(item)
    }
    return {
        "start_date": start_date,
        "end_date": end_date,
        "total_attempts": len(attempts),
        "unique_questions": len(attempted),
        "attempted_question_ids": _ordered_question_ids(attempted),
        "wrong_question_ids": _ordered_question_ids(wrong),
        "unknown_question_ids": _ordered_question_ids(unknown),
        "confident_wrong_question_ids": _ordered_question_ids(confident_wrong),
    }


def install_pt_dashboard_history_scope(goukaku_module) -> None:
    """Bind direct dashboard history helpers to the explicit PT store once."""
    if getattr(goukaku_module, "_pt_dashboard_history_scope_installed", False):
        return

    store = get_learning_history_store("pt")
    goukaku_module.get_question_attempts = store.get_question_attempts
    goukaku_module.get_weekly_question_history = (
        lambda user_id, now=None: build_pt_weekly_question_history(
            user_id, now=now, store=store
        )
    )
    goukaku_module._pt_dashboard_history_store = store
    goukaku_module._pt_dashboard_history_scope_installed = True
