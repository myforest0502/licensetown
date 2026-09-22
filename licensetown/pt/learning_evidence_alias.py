"""Reviewed semantic aliases used only for learning evidence.

This layer is intentionally separate from question_equivalence.py.  Exact
question equivalence is a stricter item-level contract used by validators and
question-bank selection.  These aliases only say that two distinct surface
questions must not count as independent weakness/repair proof.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from question_equivalence import canonicalize_question_evidence_id


_ALIAS_PATH = (
    Path(__file__).resolve().parent
    / "data"
    / "question_bank"
    / "learning_evidence_alias_groups.json"
)


def _load_aliases(path: Path = _ALIAS_PATH) -> tuple[dict[str, str], dict[str, frozenset[str]]]:
    raw = json.loads(path.read_text(encoding="utf-8-sig"))
    canonical_by_question: dict[str, str] = {}
    group_by_question: dict[str, frozenset[str]] = {}
    seen_alias_ids: set[str] = set()

    if not isinstance(raw, list):
        raise ValueError("learning evidence aliases must be an array")

    for index, record in enumerate(raw):
        label = f"learning_evidence_alias[{index}]"
        if not isinstance(record, dict):
            raise ValueError(f"{label} must be an object")
        alias_id = str(record.get("evidence_alias_id") or "")
        if not alias_id or alias_id in seen_alias_ids:
            raise ValueError(f"{label} duplicate/empty evidence_alias_id")
        seen_alias_ids.add(alias_id)
        if record.get("review_status") != "reviewed":
            raise ValueError(f"{label} must be reviewed")
        if record.get("alias_type") != "same_reviewed_source_choice":
            raise ValueError(f"{label} unsupported alias_type")
        members = [str(value) for value in record.get("question_ids") or []]
        if len(members) != 2 or len(set(members)) != 2:
            raise ValueError(f"{label} requires exactly two unique question IDs")
        canonical = str(record.get("canonical_question_id") or "")
        if canonical not in members:
            raise ValueError(f"{label} canonical_question_id must be a member")
        frozen = frozenset(members)
        for question_id in members:
            if question_id in canonical_by_question:
                raise ValueError(f"question appears in multiple learning aliases: {question_id}")
            canonical_by_question[question_id] = canonical
            group_by_question[question_id] = frozen

    return canonical_by_question, group_by_question


_CANONICAL_BY_QUESTION, _GROUP_BY_QUESTION = _load_aliases()


def canonicalize_learning_evidence_id(question_id: str | None) -> str:
    """Return the evidence identity used for weakness/repair derivation."""
    exact = canonicalize_question_evidence_id(str(question_id or ""))
    return _CANONICAL_BY_QUESTION.get(exact, exact)


def are_same_learning_evidence(
    first_question_id: str | None,
    second_question_id: str | None,
) -> bool:
    first = canonicalize_learning_evidence_id(first_question_id)
    second = canonicalize_learning_evidence_id(second_question_id)
    return bool(first and second and first == second)


def learning_evidence_alias_members(question_id: str | None) -> frozenset[str]:
    text = str(question_id or "")
    if not text:
        return frozenset()
    exact = canonicalize_question_evidence_id(text)
    return _GROUP_BY_QUESTION.get(exact, frozenset({exact}))
