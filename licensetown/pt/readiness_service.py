"""Read-only service that assembles formal readiness inputs for one learner."""

from __future__ import annotations

from typing import Any

from database import get_question_attempts
from field_evidence import build_field_evidence
from field_progress import build_field_progress
from pass_readiness import build_pass_readiness
from trial100_store import get_trial100_records


def build_pass_readiness_for_user(user_id: str) -> dict[str, Any]:
    """Build item-11 readiness from durable attempts plus Trial100 evidence."""
    user_id = str(user_id or "").strip()
    if not user_id:
        raise ValueError("user_id is required")

    attempts = get_question_attempts(user_id)
    evidence = build_field_evidence(attempts)
    progress = build_field_progress(evidence)
    trial100_records = get_trial100_records(user_id)
    return build_pass_readiness(
        attempts,
        field_evidence=evidence,
        progress=progress,
        trial100_records=trial100_records,
    )
