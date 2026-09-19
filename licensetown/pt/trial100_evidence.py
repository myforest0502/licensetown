"""Pure Trial100 evidence contract for readiness input.

This module validates and normalizes paper-based full-format Trial100 results.
It does not persist data and does not infer a passing probability or invent a
score threshold for "supportive" evidence.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Mapping


TRIAL100_TOTAL_QUESTIONS = 100
TRIAL100_TIME_LIMIT_MINUTES = 160
_ALLOWED_COMPLETION_STATUS = {"completed", "incomplete"}


def _iso_date(value: Any) -> str:
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()
    text = str(value or "").strip()
    if not text:
        raise ValueError("test_date is required")
    try:
        return date.fromisoformat(text).isoformat()
    except ValueError as exc:
        raise ValueError("test_date must be ISO YYYY-MM-DD") from exc


def normalize_trial100_record(record: Mapping[str, Any]) -> dict[str, Any]:
    """Return a validated, readiness-compatible Trial100 evidence record.

    `supportive` is accepted only as an explicit boolean assessment.  This
    contract intentionally does not derive supportive evidence from score alone.
    """
    user_id = str(record.get("user_id") or "").strip()
    source_version = str(record.get("source_version") or "").strip()
    if not user_id:
        raise ValueError("user_id is required")
    if not source_version:
        raise ValueError("source_version is required")

    total_questions = int(record.get("total_questions", TRIAL100_TOTAL_QUESTIONS))
    correct_count = int(record.get("correct_count", -1))
    if total_questions <= 0:
        raise ValueError("total_questions must be positive")
    if correct_count < 0 or correct_count > total_questions:
        raise ValueError("correct_count must be between 0 and total_questions")

    completion_status = str(record.get("completion_status") or "completed").strip()
    if completion_status not in _ALLOWED_COMPLETION_STATUS:
        raise ValueError("completion_status must be completed or incomplete")

    duration_value = record.get("duration_minutes")
    duration_minutes = None if duration_value in (None, "") else int(duration_value)
    if duration_minutes is not None and duration_minutes <= 0:
        raise ValueError("duration_minutes must be positive when recorded")

    supportive_value = record.get("supportive", False)
    if not isinstance(supportive_value, bool):
        raise ValueError("supportive must be an explicit boolean when provided")

    timed_full_format = bool(
        total_questions == TRIAL100_TOTAL_QUESTIONS
        and completion_status == "completed"
        and duration_minutes is not None
        and duration_minutes <= TRIAL100_TIME_LIMIT_MINUTES
    )

    field_breakdown = record.get("field_breakdown")
    if field_breakdown is not None and not isinstance(field_breakdown, Mapping):
        raise ValueError("field_breakdown must be a mapping when provided")

    review_summary = record.get("review_summary")
    if review_summary is not None and not isinstance(review_summary, Mapping):
        raise ValueError("review_summary must be a mapping when provided")

    return {
        "user_id": user_id,
        "test_date": _iso_date(record.get("test_date")),
        "source_version": source_version,
        "total_questions": total_questions,
        "correct_count": correct_count,
        "score_rate": correct_count / total_questions,
        "completion_status": completion_status,
        "duration_minutes": duration_minutes,
        "timed_full_format": timed_full_format,
        "supportive": supportive_value,
        "field_breakdown": dict(field_breakdown) if field_breakdown is not None else None,
        "review_summary": dict(review_summary) if review_summary is not None else None,
    }


def normalize_trial100_records(records: list[Mapping[str, Any]] | tuple[Mapping[str, Any], ...]) -> list[dict[str, Any]]:
    """Normalize records without changing order or synthesizing missing attempts."""
    return [normalize_trial100_record(record) for record in records]
