"""Pure PREREQUISITE backtrack candidate selection and coverage simulation."""

from __future__ import annotations

from collections import Counter
from typing import Any, Iterable

from prerequisite_diagnosis import (
    SOURCE_CONFIDENT_CORRECT,
    attempt_order_key,
    derive_prerequisite_diagnosis,
    is_formal_prerequisite_relation,
)


def _question_order(question_id: str) -> tuple[int, str]:
    text = str(question_id or "")
    try:
        return int(text.removeprefix("Q")), text
    except ValueError:
        return 10**9, text


def _latest_by_question(
    attempts: Iterable[dict[str, Any]], source_question_ids: set[str]
) -> dict[str, dict[str, Any]]:
    latest: dict[str, dict[str, Any]] = {}
    for attempt in sorted((dict(item) for item in attempts), key=attempt_order_key):
        question_id = str(attempt.get("question_id") or "")
        if question_id in source_question_ids:
            latest[question_id] = attempt
    return latest


def select_prerequisite_backtrack_candidate(
    diagnosis: dict[str, Any],
    relation: dict[str, Any],
    prior_attempts: Iterable[dict[str, Any]],
) -> dict[str, Any]:
    """Select one source Q deterministically without mutating saved history."""
    if not is_formal_prerequisite_relation(relation):
        raise ValueError("relation is not a formal high-confidence PREREQUISITE")
    if diagnosis.get("relation_id") != relation.get("relation_id"):
        raise ValueError("diagnosis and relation do not match")

    if diagnosis.get("source_status") == SOURCE_CONFIDENT_CORRECT:
        return {
            "backtrack": False,
            "candidate_question_id": None,
            "candidate_reason": "target_self_repair",
            "source_history_state": SOURCE_CONFIDENT_CORRECT,
        }

    source_ids = {str(item) for item in relation.get("source_question_ids", [])}
    latest = _latest_by_question(prior_attempts, source_ids)
    ranked: list[tuple[int, tuple[int, str], str, str]] = []
    for question_id in source_ids:
        attempt = latest.get(question_id)
        if attempt is None:
            rank, reason = 0, "unanswered_source"
        elif attempt.get("is_correct") is False:
            rank, reason = 1, "previously_wrong_source"
        elif attempt.get("confidence") in {2, 3}:
            rank, reason = 2, "uncertain_or_guessed_correct_source"
        else:
            rank, reason = 3, "confident_correct_source"
        ranked.append((rank, _question_order(question_id), question_id, reason))

    if not ranked:
        return {
            "backtrack": True,
            "candidate_question_id": None,
            "candidate_reason": "source_question_missing",
            "source_history_state": diagnosis.get("source_status"),
        }

    _, _, candidate, reason = min(ranked)
    return {
        "backtrack": True,
        "candidate_question_id": candidate,
        "candidate_reason": reason,
        "source_history_state": diagnosis.get("source_status"),
    }


def simulate_prerequisite_backtrack_selection(
    attempts: Iterable[dict[str, Any]],
    relations: Iterable[dict[str, Any]],
    example_limit: int = 20,
) -> dict[str, Any]:
    """Replay target errors and report static bank coverage for every relation."""
    ordered = sorted((dict(item) for item in attempts), key=attempt_order_key)
    formal = sorted(
        (dict(item) for item in relations if is_formal_prerequisite_relation(item)),
        key=lambda item: item["relation_id"],
    )
    examples: list[dict[str, Any]] = []
    relation_reports: list[dict[str, Any]] = []
    totals = Counter()

    for relation in formal:
        target_attempts = [
            item for item in ordered
            if item.get("knowledge_node_id") == relation["target_node_id"]
        ]
        target_wrong = [item for item in target_attempts if item.get("is_correct") is False]
        source_questions = sorted(set(relation.get("source_question_ids", [])), key=_question_order)
        target_questions = sorted(set(relation.get("target_question_ids", [])), key=_question_order)
        available = bool(source_questions and target_questions)
        relation_reports.append({
            "relation_id": relation["relation_id"],
            "source_node_id": relation["source_node_id"],
            "target_node_id": relation["target_node_id"],
            "source_questions": source_questions,
            "target_questions": target_questions,
            "source_candidate_available": available,
            "historical_target_attempts": len(target_attempts),
            "historical_target_wrongs": len(target_wrong),
        })

        totals["target_wrong_events"] += len(target_wrong)
        for target in target_wrong:
            target_key = attempt_order_key(target)
            prior = [
                item for item in ordered
                if item.get("user_id") == target.get("user_id")
                and attempt_order_key(item) < target_key
            ]
            diagnosis = derive_prerequisite_diagnosis(target, prior, relation)
            selection = select_prerequisite_backtrack_candidate(diagnosis, relation, prior)
            if selection["backtrack"]:
                totals["backtrack_required"] += 1
                totals[
                    "source_candidate_generated"
                    if selection["candidate_question_id"]
                    else "source_candidate_missing"
                ] += 1
            else:
                totals["target_self_repair"] += 1
            if len(examples) < max(0, example_limit):
                examples.append({
                    "relation_id": relation["relation_id"],
                    "source_node_id": relation["source_node_id"],
                    "target_node_id": relation["target_node_id"],
                    "diagnosis": diagnosis["source_status"],
                    "backtrack": selection["backtrack"],
                    "source_candidate_question_id": selection["candidate_question_id"],
                    "candidate_reason": selection["candidate_reason"],
                    "source_history_state": selection["source_history_state"],
                    "target_question_id": target.get("question_id"),
                })

    source_counts = Counter(len(item["source_questions"]) for item in relation_reports)
    target_counts = Counter(len(item["target_questions"]) for item in relation_reports)
    return {
        "target_wrong_events": totals["target_wrong_events"],
        "backtrack_required": totals["backtrack_required"],
        "source_candidate_generated": totals["source_candidate_generated"],
        "source_candidate_missing": totals["source_candidate_missing"],
        "target_self_repair": totals["target_self_repair"],
        "bank_coverage": {
            "relation_count": len(formal),
            "relations_with_source_questions": sum(
                bool(item["source_questions"]) for item in relation_reports
            ),
            "relations_with_target_questions": sum(
                bool(item["target_questions"]) for item in relation_reports
            ),
            "relations_ready_for_backtrack": sum(
                item["source_candidate_available"] for item in relation_reports
            ),
            "source_question_count_distribution": dict(sorted(source_counts.items())),
            "target_question_count_distribution": dict(sorted(target_counts.items())),
        },
        "relations": relation_reports,
        "examples": examples,
    }
