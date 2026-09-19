"""Read-only repairability audit for canonical Knowledge Nodes.

This module deliberately does not alter the formal state transition.  Candidate
paths remain diagnostic until their clinical/educational review is complete.
"""

from __future__ import annotations

from collections import defaultdict
from itertools import combinations
from typing import Any, Iterable

from knowledge_node_canonical import canonicalize_knowledge_node_id
from knowledge_node_relations import get_node_relations
from knowledge_node_repair_evidence import (
    DIFFERENT_QUESTION_STRONG,
    DIFFERENT_QUESTION_WEAK,
    classify_repair_confirmation,
)
from question_bank import get_category_name, get_category_small, get_question_tag, question_ids


STRONG_ALT = "strong_alt_question_available"
WEAK_ALT_ONLY = "weak_alt_question_only"
VALIDATED_RELATION_CANDIDATE = "validated_transfer_candidate"
WRITTEN_CANDIDATE = "written_confirmation_candidate"
SAME_QUESTION_ONLY = "same_question_only"
CURRENTLY_UNREPAIRABLE = "currently_unrepairable"


def _canonical_question_registry() -> dict[str, list[str]]:
    grouped: dict[str, list[str]] = defaultdict(list)
    for question_id in question_ids():
        raw_node = str(get_question_tag(question_id)["knowledge_node_id"])
        canonical = str(canonicalize_knowledge_node_id(raw_node))
        grouped[canonical].append(question_id)
    return dict(grouped)


def _relation_candidates() -> dict[str, list[dict[str, Any]]]:
    """Map a source concept to questions that may exercise it downstream.

    A prerequisite/transfer relation is only a candidate here.  Even high,
    reviewed_candidate metadata never becomes formal repair evidence implicitly.
    """
    result: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for relation in get_node_relations():
        source = str(canonicalize_knowledge_node_id(relation["source_node_id"]))
        target = str(canonicalize_knowledge_node_id(relation["target_node_id"]))
        result[source].append({
            "relation_id": relation["relation_id"],
            "relation_type": relation["relation_type"],
            "related_node_id": target,
            "candidate_question_ids": list(relation["target_question_ids"]),
            "confidence": relation["confidence"],
            "review_status": relation["review_status"],
            "verification_role": relation["verification_role"],
            "formally_enabled_for_repair": False,
        })
        if relation.get("bidirectional"):
            result[target].append({
                "relation_id": relation["relation_id"],
                "relation_type": relation["relation_type"],
                "related_node_id": source,
                "candidate_question_ids": list(relation["source_question_ids"]),
                "confidence": relation["confidence"],
                "review_status": relation["review_status"],
                "verification_role": relation["verification_role"],
                "formally_enabled_for_repair": False,
            })
    return dict(result)


def build_repairability_audit() -> list[dict[str, Any]]:
    """Classify all canonical Nodes without changing DB/state/selection behavior."""
    registry = _canonical_question_registry()
    relation_candidates = _relation_candidates()
    records: list[dict[str, Any]] = []
    for canonical_node_id, node_questions in sorted(registry.items()):
        strong_pairs: list[list[str]] = []
        weak_pairs: list[list[str]] = []
        tasks: set[str] = set()
        primary_abilities: set[str] = set()
        secondary_abilities: set[str] = set()
        safety: set[str] = set()
        prerequisites: set[str] = set()
        fields: set[str] = set()
        labels: set[str] = set()
        for question_id in node_questions:
            tag = get_question_tag(question_id)
            labels.add(str(tag.get("knowledge_node") or ""))
            tasks.add(str(tag.get("task") or ""))
            primary_abilities.add(str(tag.get("primary_ability") or ""))
            if tag.get("secondary_ability"):
                secondary_abilities.add(str(tag["secondary_ability"]))
            safety.add(str(tag.get("safety") or ""))
            prerequisites.update(str(item) for item in tag.get("prerequisite_nodes", []))
            fields.add(get_category_name(get_category_small(question_id)))
        for first, second in combinations(node_questions, 2):
            strength = classify_repair_confirmation(first, second)
            (strong_pairs if strength == DIFFERENT_QUESTION_STRONG else weak_pairs).append(
                [first, second]
            )

        relations = relation_candidates.get(canonical_node_id, [])
        if strong_pairs:
            classification = STRONG_ALT
        elif len(node_questions) > 1:
            classification = WEAK_ALT_ONLY
        elif relations:
            classification = VALIDATED_RELATION_CANDIDATE
        else:
            classification = SAME_QUESTION_ONLY

        # Existing written prompts can target a Node label, but PASS is not yet
        # accepted as formal repair evidence.  This is therefore shadow-only.
        written_candidate = bool(any(label.strip() for label in labels))
        confirmation_paths = ["same_question_fallback"]
        if strong_pairs:
            confirmation_paths.insert(0, "strong_alt_question")
        elif weak_pairs:
            confirmation_paths.insert(0, "weak_alt_question")
        if relations:
            confirmation_paths.extend(sorted({
                f"{candidate['relation_type'].lower()}_candidate" for candidate in relations
            }))
        if written_candidate:
            confirmation_paths.append("written_confirmation_candidate")
        records.append({
            "canonical_node_id": canonical_node_id,
            "question_ids": node_questions,
            "question_count": len(node_questions),
            "classification": classification,
            "repairable": bool(strong_pairs),
            "currently_unrepairable": not bool(strong_pairs),
            "confirmation_path": confirmation_paths,
            "confirmation_candidate_count": (
                len(strong_pairs) + len(weak_pairs) + len(relations) + int(written_candidate)
            ),
            "formal_confirmation_candidate_count": len(strong_pairs),
            "strong_alt_pairs": strong_pairs,
            "weak_alt_pairs": weak_pairs,
            "relation_candidates": relations,
            "written_confirmation_candidate": written_candidate,
            "written_formally_enabled_for_repair": False,
            "knowledge_node_labels": sorted(labels),
            "tasks": sorted(tasks),
            "primary_abilities": sorted(primary_abilities),
            "secondary_abilities": sorted(secondary_abilities),
            "safety": sorted(safety),
            "prerequisite_nodes": sorted(prerequisites),
            "fields": sorted(fields),
            "human_review_required": bool(relations) or written_candidate,
        })
    return records


def summarize_repairability(records: Iterable[dict[str, Any]]) -> dict[str, int]:
    values = list(records)
    return {
        "canonical_node_count": len(values),
        "singleton_node_count": sum(item["question_count"] == 1 for item in values),
        "multi_question_node_count": sum(item["question_count"] > 1 for item in values),
        "strong_alt_question_available_node_count": sum(
            item["classification"] == STRONG_ALT for item in values
        ),
        "weak_alt_question_only_node_count": sum(
            item["classification"] == WEAK_ALT_ONLY for item in values
        ),
        "same_question_only_node_count": sum(
            item["classification"] == SAME_QUESTION_ONLY for item in values
        ),
        "currently_unrepairable_node_count": sum(item["currently_unrepairable"] for item in values),
        "transfer_candidate_node_count": sum(
            any(candidate["relation_type"] == "TRANSFER" for candidate in item["relation_candidates"])
            for item in values
        ),
        "prerequisite_candidate_node_count": sum(
            any(candidate["relation_type"] == "PREREQUISITE" for candidate in item["relation_candidates"])
            for item in values
        ),
        "written_confirmation_candidate_node_count": sum(
            item["written_confirmation_candidate"] for item in values
        ),
        "human_review_required_node_count": sum(item["human_review_required"] for item in values),
    }


def shadow_confirmation_outcome(path: str, result: str | None = None) -> dict[str, Any]:
    """Evaluate proposed paths without returning or mutating a formal Node state."""
    normalized_path = str(path or "")
    normalized_result = str(result or "UNKNOWN").upper()
    eligible = (
        normalized_path == "strong_alt_question" and normalized_result == "PASS"
    )
    if normalized_path in {"validated_transfer", "written_confirmation"}:
        # Human/pilot validation is intentionally required before state use.
        eligible = False
    return {
        "formal_state_change": False,
        "repair_candidate": eligible,
        "remain_repairing": not eligible,
        "reason": (
            "Only an existing strong different-question PASS is formally eligible."
            if eligible
            else "Candidate, same/weak, non-PASS, or evaluator failure remains repairing."
        ),
    }
