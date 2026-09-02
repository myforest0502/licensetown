"""Compatibility adapter for deterministic read-only Phase11 Shadow judgment.

The public API stays stable for existing callers. Formal J1-J7 judgment and
symmetric evidence profiles are delegated to `phase11_formal_judgment`, which
uses current repair-cycle evidence, evaluable-answer semantics, and explicit
retention-reference attribution. Phase10 remains responsible for exact Q IDs.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Iterable

import phase11_formal_judgment as _formal


REASON_LABELS = _formal.REASON_LABELS
CONFIDENCE_RATIONALES = _formal.CONFIDENCE_RATIONALES
REASON_RANKS = _formal.REASON_RANKS

# Kept as a patchable compatibility surface for existing tests and diagnostics.
# Before delegating, the subset used by the formal engine is synchronized.
_CATALOG = dict(_formal._CATALOG)


def _sync_catalog() -> None:
    _formal._CATALOG = {
        "field_by_question": dict(_CATALOG.get("field_by_question", {})),
        "critical_nodes": set(_CATALOG.get("critical_nodes", set())),
    }


def _current_target(current_guidance: dict[str, Any] | None) -> str | None:
    recommended = (current_guidance or {}).get("recommended_study") or []
    first = recommended[0] if recommended else None
    return str(first[0]) if isinstance(first, (list, tuple)) and first else None


def _compat_profile_aliases(profile: dict[str, Any]) -> dict[str, Any]:
    """Preserve pre-formal diagnostic field names while exposing new metrics."""
    item = dict(profile)
    item.setdefault(
        "cross_question_confident_wrong_node_count",
        int(item.get("active_cross_question_confident_wrong_node_count") or 0),
    )
    item.setdefault(
        "distinct_confident_wrong_repairing_node_count",
        int(item.get("active_confident_wrong_repairing_node_count") or 0),
    )
    item.setdefault(
        "cross_question_wrong_node_count",
        int(item.get("active_cross_question_wrong_node_count") or 0),
    )
    item.setdefault(
        "repeated_weakness_node_count",
        int(item.get("active_repeated_weakness_node_count") or 0),
    )
    item.setdefault("answered_count", int(item.get("raw_answer_count") or 0))
    item.setdefault("accuracy", item.get("raw_accuracy"))
    return item


def _precomputed_retention_candidates(field_evidence: dict[str, Any]) -> list[dict[str, int]]:
    """Compatibility-only J4 facts for callers that provide no raw attempts.

    Production diagnostics pass raw attempts and therefore use formal retention
    reference attribution. This path exists only for legacy/precomputed callers.
    """
    candidates = []
    for field in field_evidence.get("fields", []):
        due = [
            item
            for item in field.get("retention_nodes", [])
            if item.get("state") == "recheck_due"
        ]
        if not due:
            continue
        overdue = [max(0, int(item.get("due_overdue_days") or 0)) for item in due]
        candidates.append({
            "field_id": int(field["field_id"]),
            "count": len(due),
            "max_overdue": max(overdue, default=0),
            "total_overdue": sum(overdue),
        })
    return sorted(
        candidates,
        key=lambda item: (
            -item["count"],
            -item["max_overdue"],
            -item["total_overdue"],
            item["field_id"],
        ),
    )


def build_field_judgment_evidence_profiles(
    attempts: Iterable[dict[str, Any]],
    field_evidence: dict[str, Any],
    *,
    as_of: datetime | None = None,
) -> dict[str, dict[str, Any]]:
    """Build symmetric J1-J7 profiles from the same formal evidence as Shadow."""
    _sync_catalog()
    attempts = [dict(item) for item in attempts]
    profiles = _formal.build_formal_field_profiles(
        attempts,
        field_evidence,
        as_of=as_of,
    )
    profiles = {
        name: _compat_profile_aliases(profile)
        for name, profile in profiles.items()
    }
    if not attempts:
        for candidate in _precomputed_retention_candidates(field_evidence):
            field_id = candidate["field_id"]
            field_name = next(
                (
                    str(item.get("field_name"))
                    for item in field_evidence.get("fields", [])
                    if int(item.get("field_id") or 0) == field_id
                ),
                str(_formal.CATEGORY_NAMES.get(field_id) or field_id),
            )
            profile = profiles.get(field_name)
            if profile and int(profile.get("reason_rank") or 99) > REASON_RANKS["recheck_due"]:
                profile["strongest_reason_code"] = "recheck_due"
                profile["strongest_reason_label"] = REASON_LABELS["recheck_due"]
                profile["reason_rank"] = REASON_RANKS["recheck_due"]
                profile["recheck_due_node_count"] = candidate["count"]
    return profiles


def build_shadow_comparison(
    current_guidance: dict[str, Any] | None,
    shadow: dict[str, Any],
    field_profiles: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Compare current and Shadow targets using symmetric formal profiles."""
    current_target = _current_target(current_guidance)
    shadow_target = shadow.get("target_field")
    current_phase = (current_guidance or {}).get("phase")
    if current_target == shadow_target and current_target is not None:
        label = (
            "same_target_same_reason"
            if shadow.get("reason_code") == "insufficient_coverage"
            and current_phase == "foundation"
            else "same_target_stronger_reason"
        )
    else:
        current_profile = (field_profiles or {}).get(str(current_target))
        shadow_profile = (field_profiles or {}).get(str(shadow_target))
        current_rank = current_profile.get("reason_rank") if current_profile else None
        shadow_rank = shadow_profile.get("reason_rank") if shadow_profile else None
        if current_rank is not None and shadow_rank is not None and shadow_rank < current_rank:
            label = "different_target_shadow_has_stronger_evidence"
        elif current_rank is not None and shadow_rank is not None and current_rank < shadow_rank:
            label = "different_target_current_has_stronger_evidence"
        else:
            label = "insufficient_evidence_to_judge"
    current_profile = (field_profiles or {}).get(str(current_target))
    shadow_profile = (field_profiles or {}).get(str(shadow_target))
    return {
        "current_target": current_target,
        "current_phase": current_phase,
        "shadow_target": shadow_target,
        "shadow_reason_code": shadow.get("reason_code"),
        "label": label,
        "current_target_formal_evidence": current_profile,
        "shadow_target_formal_evidence": shadow_profile,
        "shadow_reason_profile_consistent": bool(
            shadow_profile
            and shadow_profile.get("strongest_reason_code") == shadow.get("reason_code")
        ),
    }


def build_shadow_judgment(
    attempts: Iterable[dict[str, Any]],
    field_evidence: dict[str, Any],
    current_guidance: dict[str, Any] | None,
    *,
    as_of: datetime | None = None,
) -> dict[str, Any]:
    """Return the first matching formal Phase11 v0.1 rule in J1-J7 order."""
    _sync_catalog()
    attempts = [dict(item) for item in attempts]
    result = _formal.build_formal_shadow_judgment(
        attempts,
        field_evidence,
        current_guidance,
        as_of=as_of,
    )
    if not attempts and result.get("reason_code") == "insufficient_coverage":
        candidates = _precomputed_retention_candidates(field_evidence)
        if candidates:
            chosen = candidates[0]
            return _formal._make_result(
                intent="recheck",
                field_id=chosen["field_id"],
                question_count=10,
                route="dashboard_recommendation",
                reason_code="recheck_due",
                confidence="medium",
                evidence=[
                    f"recheck_due_nodes={chosen['count']}",
                    f"max_overdue_days={chosen['max_overdue']}",
                    f"total_overdue_days={chosen['total_overdue']}",
                    "source=precomputed_retention_compatibility",
                ],
                observations=[],
            )
    return result
