"""Reviewed question-level equivalence for learning evidence without rewriting raw Q IDs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from knowledge_node_canonical import canonicalize_knowledge_node_id


BANK_DIR = Path(__file__).resolve().parent / "data" / "question_bank"
EQUIVALENCE_PATH = BANK_DIR / "question_equivalence_groups.json"


class QuestionEquivalenceValidationError(ValueError):
    """Raised when reviewed question-equivalence master data is inconsistent."""


def _load_records(path: Path = EQUIVALENCE_PATH) -> list[dict[str, Any]]:
    raw = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(raw, list):
        raise QuestionEquivalenceValidationError("question equivalence data must be an array")
    return raw


def load_and_validate_question_equivalence(
    path: Path = EQUIVALENCE_PATH,
) -> tuple[list[dict[str, Any]], dict[str, str], dict[str, str], dict[str, frozenset[str]]]:
    records = _load_records(path)
    canonical_by_question: dict[str, str] = {}
    node_by_question: dict[str, str] = {}
    group_by_question: dict[str, frozenset[str]] = {}
    seen_equivalence_ids: set[str] = set()

    for index, record in enumerate(records):
        label = f"question_equivalence[{index}]"
        required = {
            "equivalence_id",
            "canonical_question_id",
            "canonical_knowledge_node_id",
            "question_ids",
            "equivalence_type",
            "review_status",
            "reason",
        }
        missing = required - record.keys()
        if missing:
            raise QuestionEquivalenceValidationError(f"{label} missing {sorted(missing)}")
        equivalence_id = str(record["equivalence_id"])
        if not equivalence_id or equivalence_id in seen_equivalence_ids:
            raise QuestionEquivalenceValidationError(f"{label} duplicate/empty equivalence_id")
        seen_equivalence_ids.add(equivalence_id)
        if record.get("review_status") != "reviewed":
            raise QuestionEquivalenceValidationError(f"{label} must be reviewed")
        question_ids = [str(value) for value in record.get("question_ids") or []]
        if len(question_ids) < 2 or len(question_ids) != len(set(question_ids)):
            raise QuestionEquivalenceValidationError(f"{label} needs at least two unique question IDs")
        canonical_question = str(record.get("canonical_question_id") or "")
        if canonical_question not in question_ids:
            raise QuestionEquivalenceValidationError(f"{label} canonical question must be a member")
        canonical_node = str(record.get("canonical_knowledge_node_id") or "")
        if not canonical_node:
            raise QuestionEquivalenceValidationError(f"{label} canonical Node is empty")
        members = frozenset(question_ids)
        for question_id in question_ids:
            if question_id in canonical_by_question:
                raise QuestionEquivalenceValidationError(
                    f"question appears in multiple equivalence groups: {question_id}"
                )
            canonical_by_question[question_id] = canonical_question
            node_by_question[question_id] = canonical_node
            group_by_question[question_id] = members

    return records, canonical_by_question, node_by_question, group_by_question


_RECORDS, _CANONICAL_BY_QUESTION, _NODE_BY_QUESTION, _GROUP_BY_QUESTION = (
    load_and_validate_question_equivalence()
)


def get_question_equivalence_groups() -> list[dict[str, Any]]:
    """Return a copy-safe representation of reviewed equivalence groups."""
    return [dict(record) for record in _RECORDS]


def canonicalize_question_evidence_id(question_id: str | None) -> str:
    """Resolve exact provenance repeats to one stable evidence identity."""
    text = str(question_id or "")
    return _CANONICAL_BY_QUESTION.get(text, text)


def equivalent_question_ids(question_id: str | None) -> frozenset[str]:
    """Return every raw Q ID in the reviewed equivalence group, or the Q itself."""
    text = str(question_id or "")
    if not text:
        return frozenset()
    return _GROUP_BY_QUESTION.get(text, frozenset({text}))


def are_equivalent_questions(first_question_id: str | None, second_question_id: str | None) -> bool:
    first = str(first_question_id or "")
    second = str(second_question_id or "")
    return bool(first and second and canonicalize_question_evidence_id(first) == canonicalize_question_evidence_id(second))


def canonicalize_question_evidence_node(
    question_id: str | None,
    raw_node_id: str | None,
) -> str | None:
    """Return the reviewed evidence Node for an exact repeat, else normal Node canonicalization.

    Raw persisted attempt Node IDs are never rewritten. This function only controls
    derived learning evidence so an identical official item cannot become independent
    evidence merely because it was imported under a different historical Node.
    """
    question = str(question_id or "")
    reviewed_node = _NODE_BY_QUESTION.get(question)
    if reviewed_node:
        return canonicalize_knowledge_node_id(reviewed_node)
    return canonicalize_knowledge_node_id(raw_node_id)
