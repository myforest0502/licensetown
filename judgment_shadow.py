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


def build_field_judgment_evidence_profiles(
    attempts: Iterable[dict[str, Any]],
    field_evidence: dict[str, Any],
    *,
    as_of: datetime | None = None,
) -> dict[str, dict[str, Any]]:
    """Build symmetric J1-J7 profiles from the same formal evidence as Shadow."""
    _sync_catalog()
    return _formal.build_formal_field_profiles(
        attempts,
        field_evidence,
        as_of=as_of,
    )


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
    return _formal.build_formal_shadow_judgment(
        attempts,
        field_evidence,
        current_guidance,
        as_of=as_of,
    )
