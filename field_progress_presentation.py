"""Presentation-only adapter for the opt-in Field Progress UI preview."""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import Any, Iterable, Mapping

from field_evidence import build_field_evidence
from field_progress import build_field_progress


STATE_LABELS = {
    "unseen": "未着手", "checking": "確認中", "repairing": "修復中",
    "repaired": "修復済み", "recheck_due": "再確認待ち", "stable": "定着",
}


def format_progress_percent(score: float) -> str:
    """Format a raw 0..1 score without feeding rounding back into calculation."""
    value = max(0.0, float(score))
    if value == 0:
        return "0%"
    percent = value * 100
    if percent < 1:
        return "1%未満"
    rounded = Decimal(str(percent)).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    return f"{int(rounded)}%"


def build_field_progress_presentation(
    attempts: Iterable[dict[str, Any]],
    *,
    legacy_fields: Iterable[Mapping[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Return all 18 fields using the formal Evidence -> Progress pipeline."""
    evidence = build_field_evidence(attempts)
    progress = build_field_progress(evidence)
    evidence_by_id: Mapping[int, dict[str, Any]] = {
        item["field_id"]: item for item in evidence["fields"]
    }
    legacy_by_name = {
        str(item["name"]): item for item in (legacy_fields or ())
    }
    result = []
    for item in progress["fields"]:
        source = evidence_by_id[item["field_id"]]
        legacy = legacy_by_name.get(item["field_name"])
        accuracy_percent = (
            int(legacy["accuracy"])
            if legacy is not None and legacy.get("learned")
            else None
        )
        result.append({
            "field_id": item["field_id"], "name": item["field_name"],
            "answer_count": (
                int(legacy["answered_count"])
                if legacy is not None else source["question_answer_count"]
            ),
            "progress_raw": item["field_progress_score"],
            "progress_display": format_progress_percent(item["field_progress_score"]),
            "coverage_raw": item["node_coverage"],
            "coverage_display": format_progress_percent(item["node_coverage"]),
            "accuracy_raw": (
                accuracy_percent / 100 if accuracy_percent is not None else None
            ),
            "accuracy_display": (
                "--" if accuracy_percent is None else f"{accuracy_percent}%"
            ),
            "state_counts": dict(item["state_counts"]),
            "state_labels": dict(STATE_LABELS),
        })
    return result
