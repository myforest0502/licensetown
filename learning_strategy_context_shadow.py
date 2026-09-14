"""Pure helpers for observed recommendation-plan concentration context.

This module is shadow/audit-only. It never reads databases, never selects
questions and never grants Production authority.  Its purpose is to convert
already-observed completed recommendation sessions into the 30-question block
context consumed by Stage D/E without inventing completion from plan goals.
"""
from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

VERSION = "learning_strategy_context_shadow_v0.1"
BLOCK_SIZE = 30


def _count(value: Any, name: str) -> int:
    try:
        number = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be an integer") from exc
    if number < 0 or str(value).strip() not in {str(number), f"{number}.0"}:
        raise ValueError(f"{name} must be a non-negative integer")
    return number


def derive_recommendation_plan_context(
    observations: Iterable[Mapping[str, Any]],
) -> dict[str, Any]:
    """Derive consecutive-field block context from completed recommendation work.

    Required input per chronological plan observation:
      - field_id: formal 1-18 field id
      - completed_recommendation_questions: questions actually completed in
        dashboard-recommendation sessions after this plan and before the next plan.

    ``goal`` may be present for audit display, but is deliberately not used as
    completion evidence.  The context for each plan is calculated *before* adding
    work completed after that plan, so no future information leaks into the
    recommendation-time concentration penalty.

    This helper does not derive ``additional_blocks_completed`` because that value
    has a different semantic contract (post-weakness additional training) and
    cannot be reconstructed merely from generic recommendation history.
    """
    rows = []
    current_field: int | None = None
    streak_questions = 0
    max_streak_questions = 0
    max_streak_blocks_after = 0

    for index, source in enumerate(observations):
        field_id = _count(source.get("field_id"), "field_id")
        if field_id not in range(1, 19):
            raise ValueError("field_id must be in 1..18")
        completed = _count(
            source.get("completed_recommendation_questions", 0),
            "completed_recommendation_questions",
        )
        goal = source.get("goal")
        if goal is not None:
            _count(goal, "goal")

        if field_id != current_field:
            streak_questions = 0
            current_field = field_id

        before_questions = streak_questions
        before_blocks = before_questions // BLOCK_SIZE
        streak_questions += completed
        after_blocks = streak_questions // BLOCK_SIZE
        max_streak_questions = max(max_streak_questions, streak_questions)
        max_streak_blocks_after = max(max_streak_blocks_after, after_blocks)

        rows.append(
            {
                "plan_index": index,
                "field_id": field_id,
                "goal": goal,
                "completed_recommendation_questions": completed,
                "observed_same_field_completed_questions_before": before_questions,
                "consecutive_field_blocks": before_blocks,
                "observed_same_field_completed_questions_after": streak_questions,
                "completed_30q_equivalent_after": after_blocks,
                "remaining_questions_to_next_30q_block_after": (
                    0 if streak_questions % BLOCK_SIZE == 0
                    else BLOCK_SIZE - streak_questions % BLOCK_SIZE
                ),
                "additional_blocks_completed": None,
                "additional_blocks_completed_available": False,
                "shadow_only": True,
                "selection_authority": False,
            }
        )

    return {
        "version": VERSION,
        "shadow_only": True,
        "selection_authority": False,
        "block_size": BLOCK_SIZE,
        "plan_count": len(rows),
        "max_observed_same_field_completed_questions": max_streak_questions,
        "max_completed_30q_equivalent_after": max_streak_blocks_after,
        "rows": rows,
    }
