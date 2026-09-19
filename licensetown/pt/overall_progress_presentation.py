"""Presentation-only adapter for the opt-in Overall Progress UI preview."""

from __future__ import annotations

from typing import Any, Mapping

from field_progress_presentation import STATE_LABELS, format_progress_percent


def build_overall_progress_presentation(
    progress: Mapping[str, Any],
    *,
    overall_accuracy_percent: int | float | None = None,
) -> dict[str, Any]:
    """Format the formal unique-canonical-Node Overall calculation."""
    overall = progress["overall"]
    total = int(overall["total_unique_canonical_nodes"])
    touched = int(overall["touched_unique_canonical_nodes"])
    counts = {key: int(value) for key, value in overall["state_counts"].items()}
    coverage = touched / total if total else 0.0
    repair_completed = (
        counts["repaired"] + counts["recheck_due"] + counts["stable"]
    ) / total if total else 0.0
    stable = counts["stable"] / total if total else 0.0
    raw = float(overall["overall_progress_score"])
    return {
        "progress_raw": raw,
        "progress_display": format_progress_percent(raw),
        "coverage_raw": coverage,
        "coverage_display": format_progress_percent(coverage),
        "repair_completed_raw": repair_completed,
        "repair_completed_display": format_progress_percent(repair_completed),
        "stable_raw": stable,
        "stable_display": format_progress_percent(stable),
        "total_unique_canonical_nodes": total,
        "touched_unique_canonical_nodes": touched,
        "state_counts": counts,
        "state_labels": dict(STATE_LABELS),
        "accuracy_display": (
            "--" if overall_accuracy_percent is None
            else f"{round(float(overall_accuracy_percent))}%"
        ),
    }
