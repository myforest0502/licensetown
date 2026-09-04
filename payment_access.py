"""Centralized LicenseTown free/paid access policy.

The policy is provider-agnostic: learning routes ask about LicenseTown feature
keys, never Stripe state. Public enforcement remains rollout-gated until the
sale-safe launch work is complete.
"""

from __future__ import annotations

import os
from typing import Any

from payment_entitlement import can_use_paid_core


FREE_FIRST_FIVE = "study_first_five"
FREE_NEXT_ACTION = "next_action"
PAID_ADAPTIVE_FULL = "adaptive_learning_full"
PAID_DASHBOARD_FULL = "dashboard_full"
PAID_SUPPORTER_FULL = "supporter_full"

_FREE_FEATURES = {FREE_FIRST_FIVE, FREE_NEXT_ACTION}
_PAID_FEATURES = {PAID_ADAPTIVE_FULL, PAID_DASHBOARD_FULL, PAID_SUPPORTER_FULL}


def paid_access_enforcement_enabled() -> bool:
    """Return whether the commercial access boundary is actively enforced."""
    return str(os.getenv("ENABLE_PAID_ACCESS_ENFORCEMENT") or "").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


def access_decision(
    user_id: str,
    feature: str,
    *,
    enforce: bool | None = None,
) -> dict[str, Any]:
    """Return one auditable access decision without provider conditionals.

    Unknown features fail closed when enforcement is active. Before launch,
    enforcement defaults off so existing learners are not accidentally locked
    out while the commercial contract is still being finalized.
    """
    user_id = str(user_id or "").strip()
    feature = str(feature or "").strip()
    if not user_id:
        return {"allowed": False, "feature": feature, "reason": "missing_user"}
    if feature in _FREE_FEATURES:
        return {"allowed": True, "feature": feature, "reason": "free_floor"}

    active = paid_access_enforcement_enabled() if enforce is None else bool(enforce)
    if not active:
        return {"allowed": True, "feature": feature, "reason": "rollout_disabled"}
    if feature not in _PAID_FEATURES:
        return {"allowed": False, "feature": feature, "reason": "unknown_feature"}
    if can_use_paid_core(user_id):
        return {"allowed": True, "feature": feature, "reason": "paid_entitlement"}
    return {"allowed": False, "feature": feature, "reason": "paid_required"}


def can_access(user_id: str, feature: str, *, enforce: bool | None = None) -> bool:
    return bool(access_decision(user_id, feature, enforce=enforce)["allowed"])
