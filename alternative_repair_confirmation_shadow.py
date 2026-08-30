"""Build clinically reviewable, fail-closed alternative-confirmation packets.

Nothing in this module changes formal Node state, Adaptive selection, or a DB.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from knowledge_node_repairability import build_repairability_audit
from question_bank import (
    CATEGORY_NAMES,
    get_answer,
    get_category_name,
    get_category_small,
    get_explanation,
    get_question,
    get_question_tag,
)


SHADOW_RESULTS = {"PASS", "PARTIAL", "FAIL", "UNKNOWN"}


def _question_packet(question_id: str) -> dict[str, Any]:
    question = get_question(question_id)
    tag = get_question_tag(question_id)
    answer = get_answer(question_id)
    explanation = get_explanation(question_id)
    return {
        "question_id": question_id,
        "question_text": question["question_text"],
        "display_answer": answer["display_answer"],
        "explanation": explanation["explanation"],
        "task": tag["task"],
        "primary_ability": tag["primary_ability"],
        "secondary_ability": tag.get("secondary_ability"),
        "prerequisite_nodes": tag.get("prerequisite_nodes", []),
        "safety": tag["safety"],
    }


def build_relation_review_packets() -> list[dict[str, Any]]:
    """Consolidate the 13 relation rows into 11 source-Node review packets."""
    nodes = [item for item in build_repairability_audit() if item["relation_candidates"]]
    packets = []
    for item in nodes:
        source_question = item["question_ids"][0]
        candidates = []
        for candidate in item["relation_candidates"]:
            candidates.append({
                **candidate,
                "candidate_questions": [
                    _question_packet(question_id)
                    for question_id in candidate["candidate_question_ids"]
                ],
                "why_it_may_confirm": (
                    "The relation metadata says the candidate question requires or transfers "
                    "the repair target concept, but that claim still needs human review."
                ),
                "false_positive_concern": (
                    "A learner may answer from the target question's surrounding knowledge "
                    "without demonstrating the source Node itself."
                ),
            })
        packets.append({
            "repair_target_node_id": item["canonical_node_id"],
            "repair_target_labels": item["knowledge_node_labels"],
            "source_question": _question_packet(source_question),
            "candidate_confirmations": candidates,
            "recommended_decision": "UNCERTAIN",
            "human_review_required": True,
            "formal_repair_enabled": False,
        })
    return packets


def select_singleton_review_sample(sample_size: int = 30) -> list[dict[str, Any]]:
    """Select a deterministic, field-balanced singleton sample."""
    singleton = [
        item for item in build_repairability_audit()
        if item["question_count"] == 1 and not item["repairable"]
    ]
    by_field: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in singleton:
        by_field[item["fields"][0]].append(item)
    selected: list[dict[str, Any]] = []
    used: set[str] = set()
    # Every formal field gets one representative first.
    for field in CATEGORY_NAMES.values():
        candidates = by_field[field]
        choice = next(
            (item for item in candidates if any(level != "none" for level in item["safety"])),
            candidates[0],
        )
        selected.append(choice)
        used.add(choice["canonical_node_id"])
    # Fill remaining slots round-robin while favouring new task/ability demands.
    seen_demands = {
        (tuple(item["tasks"]), tuple(item["primary_abilities"])) for item in selected
    }
    while len(selected) < sample_size:
        added = False
        for field in CATEGORY_NAMES.values():
            choices = [item for item in by_field[field] if item["canonical_node_id"] not in used]
            if not choices:
                continue
            choice = next(
                (
                    item for item in choices
                    if (tuple(item["tasks"]), tuple(item["primary_abilities"])) not in seen_demands
                ),
                choices[0],
            )
            selected.append(choice)
            used.add(choice["canonical_node_id"])
            seen_demands.add((tuple(choice["tasks"]), tuple(choice["primary_abilities"])))
            added = True
            if len(selected) == sample_size:
                break
        if not added:
            break
    return selected


def build_written_review_packets(sample_size: int = 30) -> list[dict[str, Any]]:
    packets = []
    for item in select_singleton_review_sample(sample_size):
        question_id = item["question_ids"][0]
        source = _question_packet(question_id)
        label = item["knowledge_node_labels"][0]
        reference = source["explanation"]
        packets.append({
            "canonical_node_id": item["canonical_node_id"],
            "field": get_category_name(get_category_small(question_id)),
            "safety": source["safety"],
            "task": source["task"],
            "primary_ability": source["primary_ability"],
            "source_question_id": question_id,
            "source_display_answer": source["display_answer"],
            "knowledge_node_label": label,
            "written_prompt": (
                f"「{label}」について、正答の記号や選択肢を使わず、"
                "判断の根拠となる中心概念を1〜2文で説明してくれ。"
            ),
            "rubric": {
                "pass_required_elements": [label, reference],
                "partial_condition": (
                    "Nodeの中心概念に触れるが、根拠・因果・適用条件のいずれかが不足する。"
                ),
                "fail_condition": "中心概念と異なる、無関係、または正答記号のみである。",
                "medical_critical_error": (
                    "正式解説の主要な因果関係・方向・適応を逆に説明する。"
                ),
                "accepted_expression_guidance": (
                    "用語の完全一致は求めず、正式解説と同じ中心概念と因果があれば許容する。"
                ),
                "reference_explanation": reference,
            },
            "deterministic_cases": [
                {"kind": "clear_correct", "answer": reference, "expected": "PASS"},
                {"kind": "missing_essence", "answer": label, "expected": "PARTIAL"},
                {
                    "kind": "plausible_wrong",
                    "answer": "主要な因果関係は正式解説と逆である。",
                    "expected": "FAIL",
                },
                {
                    "kind": "memorized_choice_only",
                    "answer": source["display_answer"],
                    "expected": "FAIL",
                },
                {"kind": "unrelated", "answer": "今日は天気が良い。", "expected": "FAIL"},
                {"kind": "empty", "answer": "", "expected": "UNKNOWN"},
            ],
            "formal_repair_enabled": False,
        })
    return packets


def evaluate_deterministic_shadow_case(
    packet: dict[str, Any], case: dict[str, Any]
) -> dict[str, Any]:
    """Evaluate controlled fixtures independently of their expected labels.

    This deliberately narrow oracle verifies fail-closed plumbing; it is not an
    evaluator for arbitrary learner prose and cannot authorize a state change.
    """
    answer = str(case.get("answer") or "").strip()
    if not answer:
        result = "UNKNOWN"
    elif answer == str(packet["source_display_answer"]):
        result = "FAIL"
    elif answer == str(packet["rubric"]["reference_explanation"]).strip():
        result = "PASS"
    elif answer == str(packet["knowledge_node_label"]).strip():
        result = "PARTIAL"
    else:
        result = "FAIL"
    return {
        "shadow_result": result,
        "formal_state_change": False,
        "remain_repairing": True,
    }


def fail_closed_shadow_evaluation(result: str | None) -> dict[str, Any]:
    """Keep every external evaluator result shadow-only, including PASS."""
    normalized = str(result or "UNKNOWN").upper()
    if normalized not in SHADOW_RESULTS:
        normalized = "UNKNOWN"
    return {
        "shadow_result": normalized,
        "formal_state_change": False,
        "remain_repairing": True,
    }


def build_shadow_review_artifact() -> dict[str, Any]:
    relation_packets = build_relation_review_packets()
    written_packets = build_written_review_packets()
    strong_references = [
        {
            "canonical_node_id": item["canonical_node_id"],
            "question_ids": item["question_ids"],
            "strong_alt_pairs": item["strong_alt_pairs"],
            "written_is_not_assumed_equivalent": True,
        }
        for item in build_repairability_audit()
        if item["repairable"]
    ]
    return {
        "version": "0.1-shadow",
        "relation_review_packets": relation_packets,
        "singleton_written_review_packets": written_packets,
        "strong_alt_reference_nodes": strong_references,
        "safety": {
            "formal_state_changes": 0,
            "adaptive_changes": 0,
            "database_writes": 0,
            "production_api_calls": 0,
        },
    }
