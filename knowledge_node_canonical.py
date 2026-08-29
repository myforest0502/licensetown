"""Canonical Knowledge Node aliases with backward-compatible raw ID storage."""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any, Iterable


BANK_DIR = Path(__file__).resolve().parent / "data" / "question_bank"
CANONICAL_MAP_PATH = BANK_DIR / "knowledge_node_canonical_map.json"


class KnowledgeNodeCanonicalValidationError(ValueError):
    """Raised when canonical alias master data is inconsistent."""


def _read_array(path: Path) -> list[dict[str, Any]]:
    records = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(records, list):
        raise KnowledgeNodeCanonicalValidationError(f"{path.name} must be an array")
    return records


def load_and_validate_canonical_map(
    bank_dir: Path = BANK_DIR,
) -> tuple[list[dict[str, Any]], dict[str, str]]:
    records = _read_array(bank_dir / "knowledge_node_canonical_map.json")
    nodes = _read_array(bank_dir / "knowledge_nodes.json")
    candidates = _read_array(bank_dir / "knowledge_node_merge_candidates.json")
    reviews = _read_array(bank_dir / "same_node_review_v0.2.json")
    node_ids = {str(item.get("knowledge_node_id")) for item in nodes}
    candidates_by_id = {str(item.get("candidate_id")): item for item in candidates}
    reviews_by_id = {str(item.get("candidate_id")): item for item in reviews}
    aliases: dict[str, str] = {}
    seen_candidates: set[str] = set()
    canonical_ids = [str(item.get("canonical_node_id")) for item in records]
    if len(canonical_ids) != len(set(canonical_ids)):
        raise KnowledgeNodeCanonicalValidationError("duplicate canonical Node")
    canonical_id_set = set(canonical_ids)

    def reviewed_nodes(candidate_id: str, path: str) -> set[str]:
        candidate = candidates_by_id.get(candidate_id)
        if candidate is not None:
            if candidate.get("review_status") != "reviewed":
                raise KnowledgeNodeCanonicalValidationError(f"{path} is not reviewed")
            return {str(item) for item in candidate.get("node_ids", [])}
        review = reviews_by_id.get(candidate_id)
        if (
            review is None
            or review.get("review_status") != "reviewed"
            or review.get("aoi_decision") != "SAME_NODE_APPROVED"
        ):
            raise KnowledgeNodeCanonicalValidationError(f"{path} is not Aoi-approved")
        canonical = str(review.get("canonical_node_id"))
        return {canonical, *(str(item) for item in review.get("alias_node_ids", []))}

    for index, record in enumerate(records):
        path = f"canonical_map[{index}]"
        required = {
            "candidate_id", "canonical_node_id", "alias_node_ids",
            "canonical_label", "selection_rule", "reason",
        }
        missing = required - record.keys()
        if missing:
            raise KnowledgeNodeCanonicalValidationError(f"{path} missing {sorted(missing)}")
        candidate_id = str(record["candidate_id"])
        if candidate_id in seen_candidates:
            raise KnowledgeNodeCanonicalValidationError(f"duplicate candidate: {candidate_id}")
        seen_candidates.add(candidate_id)
        canonical = str(record["canonical_node_id"])
        alias_ids = [str(item) for item in record["alias_node_ids"]]
        if not alias_ids or len(alias_ids) != len(set(alias_ids)):
            raise KnowledgeNodeCanonicalValidationError(f"{path} aliases must be unique")
        combined = {canonical, *alias_ids}
        source_candidate_ids = [
            str(item) for item in record.get("source_candidate_ids", [candidate_id])
        ]
        if not source_candidate_ids or len(source_candidate_ids) != len(set(source_candidate_ids)):
            raise KnowledgeNodeCanonicalValidationError(f"{path} source candidates must be unique")
        reviewed_combined: set[str] = set()
        for source_id in source_candidate_ids:
            reviewed_combined.update(reviewed_nodes(source_id, path))
        if combined != reviewed_combined:
            raise KnowledgeNodeCanonicalValidationError(f"{path} does not match candidate Nodes")
        if any(node_id not in node_ids for node_id in combined):
            raise KnowledgeNodeCanonicalValidationError(f"{path} references unknown Node")
        selection_rule = record["selection_rule"]
        if selection_rule == "lowest_numeric_existing_node_id":
            if canonical != min(combined, key=lambda value: int(value[2:])):
                raise KnowledgeNodeCanonicalValidationError(f"{path} canonical is not the lowest ID")
        elif selection_rule == "existing_canonical_root_is_stable":
            original = candidates_by_id.get(candidate_id)
            if not original or canonical not in {str(item) for item in original.get("node_ids", [])}:
                raise KnowledgeNodeCanonicalValidationError(
                    f"{path} stable root is not present in the original reviewed candidate"
                )
        else:
            raise KnowledgeNodeCanonicalValidationError(f"{path} has invalid selection rule")
        for alias in alias_ids:
            if alias in aliases or alias in canonical_id_set:
                raise KnowledgeNodeCanonicalValidationError(f"duplicate or cyclic alias: {alias}")
            aliases[alias] = canonical
    if any(canonical in aliases for canonical in aliases.values()):
        raise KnowledgeNodeCanonicalValidationError("alias chain or cycle detected")
    return records, aliases


_CANONICAL_RECORDS, _ALIASES = load_and_validate_canonical_map()


def get_knowledge_node_canonical_map() -> list[dict[str, Any]]:
    return copy.deepcopy(_CANONICAL_RECORDS)


def canonicalize_knowledge_node_id(node_id: str | None) -> str | None:
    """Resolve reviewed aliases while leaving canonical and unknown IDs unchanged."""
    if node_id is None:
        return None
    text = str(node_id)
    return _ALIASES.get(text, text)


def group_attempts_by_canonical_node(
    attempts: Iterable[dict[str, Any]],
) -> dict[tuple[str | None, str | None], list[dict[str, Any]]]:
    """Group raw persisted attempts without rewriting their original Node IDs."""
    grouped: dict[tuple[str | None, str | None], list[dict[str, Any]]] = {}
    for attempt in attempts:
        item = dict(attempt)
        canonical = canonicalize_knowledge_node_id(item.get("knowledge_node_id"))
        item["canonical_knowledge_node_id"] = canonical
        grouped.setdefault((item.get("user_id"), canonical), []).append(item)
    return grouped


def is_cross_question_evidence(
    first_attempt: dict[str, Any], second_attempt: dict[str, Any]
) -> bool:
    """Require the same canonical Node and two different non-empty question IDs."""
    first_node = canonicalize_knowledge_node_id(first_attempt.get("knowledge_node_id"))
    second_node = canonicalize_knowledge_node_id(second_attempt.get("knowledge_node_id"))
    first_question = str(first_attempt.get("question_id") or "")
    second_question = str(second_attempt.get("question_id") or "")
    return bool(
        first_node
        and first_node == second_node
        and first_question
        and second_question
        and first_question != second_question
    )
