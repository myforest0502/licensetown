"""Knowledge Node relation candidates: immutable JSON loading and validation only."""

from __future__ import annotations

import copy
import json
import re
from pathlib import Path


QUESTION_BANK_DIR = Path(__file__).resolve().parent / "data" / "question_bank"
RELATION_TYPES = {"PREREQUISITE", "TRANSFER"}
CONFIDENCE_VALUES = {"high", "medium", "low"}
RELATION_REVIEW_STATUSES = {
    "reviewed_candidate", "pending_review", "reviewed", "rejected",
}
VERIFICATION_ROLES = {"diagnostic_only", "repair_support", "transfer_check"}
MERGE_REVIEW_STATUSES = {"pending_clinical_review", "reviewed", "rejected"}


class KnowledgeNodeRelationValidationError(ValueError):
    """Raised when relation master data violates its formal invariants."""


def _read_json_array(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, list):
        raise KnowledgeNodeRelationValidationError(f"{path.name} must contain an array")
    return data


def _formal_ids(bank_dir: Path) -> tuple[set[str], set[str]]:
    nodes = _read_json_array(bank_dir / "knowledge_nodes.json")
    questions = _read_json_array(bank_dir / "questions.json")
    return (
        {str(node.get("knowledge_node_id", "")) for node in nodes},
        {str(question.get("id", "")) for question in questions},
    )


def validate_node_relations(
    relations: list[dict], node_ids: set[str], question_ids: set[str]
) -> None:
    required = {
        "relation_id", "relation_type", "source_node_id", "target_node_id",
        "bidirectional", "verification_role", "confidence", "review_status",
        "evidence", "source_question_ids", "target_question_ids", "version",
    }
    seen_ids: set[str] = set()
    seen_relations: set[tuple] = set()
    for index, relation in enumerate(relations):
        path = f"relations[{index}]"
        if not isinstance(relation, dict):
            raise KnowledgeNodeRelationValidationError(f"{path} must be an object")
        missing = required - relation.keys()
        if missing:
            raise KnowledgeNodeRelationValidationError(f"{path} missing: {sorted(missing)}")
        relation_id = relation["relation_id"]
        if not isinstance(relation_id, str) or not re.fullmatch(r"KNR\d{4}", relation_id):
            raise KnowledgeNodeRelationValidationError(f"{path} has invalid relation_id")
        if relation_id in seen_ids:
            raise KnowledgeNodeRelationValidationError(f"duplicate relation_id: {relation_id}")
        seen_ids.add(relation_id)
        if relation["relation_type"] not in RELATION_TYPES:
            raise KnowledgeNodeRelationValidationError(f"{path} has invalid relation_type")
        source = relation["source_node_id"]
        target = relation["target_node_id"]
        if source not in node_ids or target not in node_ids:
            raise KnowledgeNodeRelationValidationError(f"{path} references an unknown Node")
        if source == target:
            raise KnowledgeNodeRelationValidationError(f"{path} source and target must differ")
        if not isinstance(relation["bidirectional"], bool):
            raise KnowledgeNodeRelationValidationError(f"{path} bidirectional must be boolean")
        if relation["confidence"] not in CONFIDENCE_VALUES:
            raise KnowledgeNodeRelationValidationError(f"{path} has invalid confidence")
        if relation["review_status"] not in RELATION_REVIEW_STATUSES:
            raise KnowledgeNodeRelationValidationError(f"{path} has invalid review_status")
        if relation["verification_role"] not in VERIFICATION_ROLES:
            raise KnowledgeNodeRelationValidationError(f"{path} has invalid verification_role")
        relation_nodes = tuple(sorted((source, target))) if relation["bidirectional"] else (source, target)
        relation_key = (
            relation["relation_type"], *relation_nodes, relation["bidirectional"],
        )
        if relation_key in seen_relations:
            raise KnowledgeNodeRelationValidationError(f"duplicate relation: {relation_key}")
        seen_relations.add(relation_key)
        for field in ("source_question_ids", "target_question_ids"):
            values = relation[field]
            if not isinstance(values, list) or not values:
                raise KnowledgeNodeRelationValidationError(f"{path}.{field} must be non-empty")
            if len(values) != len(set(values)) or any(value not in question_ids for value in values):
                raise KnowledgeNodeRelationValidationError(f"{path}.{field} has invalid Q references")


def validate_merge_candidates(
    candidates: list[dict], node_ids: set[str], question_ids: set[str]
) -> None:
    required = {
        "candidate_id", "node_ids", "question_ids", "topic", "confidence",
        "review_status", "reason",
    }
    seen_ids: set[str] = set()
    for index, candidate in enumerate(candidates):
        path = f"merge_candidates[{index}]"
        if not isinstance(candidate, dict):
            raise KnowledgeNodeRelationValidationError(f"{path} must be an object")
        missing = required - candidate.keys()
        if missing:
            raise KnowledgeNodeRelationValidationError(f"{path} missing: {sorted(missing)}")
        candidate_id = candidate["candidate_id"]
        if not isinstance(candidate_id, str) or not re.fullmatch(r"KNC\d{4}", candidate_id):
            raise KnowledgeNodeRelationValidationError(f"{path} has invalid candidate_id")
        if candidate_id in seen_ids:
            raise KnowledgeNodeRelationValidationError(f"duplicate candidate_id: {candidate_id}")
        seen_ids.add(candidate_id)
        nodes = candidate["node_ids"]
        if not isinstance(nodes, list) or len(nodes) < 2 or len(nodes) != len(set(nodes)):
            raise KnowledgeNodeRelationValidationError(f"{path}.node_ids must contain unique Nodes")
        if any(node_id not in node_ids for node_id in nodes):
            raise KnowledgeNodeRelationValidationError(f"{path}.node_ids references an unknown Node")
        questions = candidate["question_ids"]
        if not isinstance(questions, list) or not questions or len(questions) != len(set(questions)):
            raise KnowledgeNodeRelationValidationError(f"{path}.question_ids must be unique")
        if any(question_id not in question_ids for question_id in questions):
            raise KnowledgeNodeRelationValidationError(f"{path}.question_ids has an unknown Q")
        if candidate["confidence"] not in CONFIDENCE_VALUES:
            raise KnowledgeNodeRelationValidationError(f"{path} has invalid confidence")
        if candidate["review_status"] not in MERGE_REVIEW_STATUSES:
            raise KnowledgeNodeRelationValidationError(f"{path} has invalid review_status")


def load_node_relation_data(bank_dir: Path = QUESTION_BANK_DIR) -> tuple[list[dict], list[dict]]:
    node_ids, question_ids = _formal_ids(bank_dir)
    relations = _read_json_array(bank_dir / "knowledge_node_relations.json")
    candidates = _read_json_array(bank_dir / "knowledge_node_merge_candidates.json")
    validate_node_relations(relations, node_ids, question_ids)
    validate_merge_candidates(candidates, node_ids, question_ids)
    return relations, candidates


_NODE_RELATIONS, _MERGE_CANDIDATES = load_node_relation_data()


def get_node_relations() -> list[dict]:
    return copy.deepcopy(_NODE_RELATIONS)


def get_reviewed_node_relations() -> list[dict]:
    """Return only high-confidence relations approved for formal read access."""
    return copy.deepcopy([
        relation for relation in _NODE_RELATIONS
        if relation["confidence"] == "high"
        and relation["review_status"] in {"reviewed", "reviewed_candidate"}
    ])


def get_node_merge_candidates() -> list[dict]:
    return copy.deepcopy(_MERGE_CANDIDATES)
