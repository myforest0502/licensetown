"""Structured, fail-closed AI shadow validation for alternative repair checks."""

from __future__ import annotations

import json
from collections import Counter
from typing import Any, Callable

from alternative_repair_confirmation_shadow import build_shadow_review_artifact
from knowledge_node_repairability import build_repairability_audit
from question_bank import get_answer, get_category_name, get_category_small, get_explanation, get_question_tag


VERDICTS = {"PASS", "PARTIAL", "FAIL", "UNKNOWN"}
DEFAULT_REPEAT_COUNT = 2
DEFAULT_MODEL = "gpt-4.1-mini"


def _strong_reference_packet(node: dict[str, Any]) -> dict[str, Any]:
    question_id = node["question_ids"][0]
    tag = get_question_tag(question_id)
    label = str(tag["knowledge_node"])
    explanation = str(get_explanation(question_id)["explanation"])
    return {
        "canonical_node_id": node["canonical_node_id"],
        "field": get_category_name(get_category_small(question_id)),
        "safety": tag["safety"],
        "task": tag["task"],
        "primary_ability": tag["primary_ability"],
        "source_question_id": question_id,
        "source_display_answer": get_answer(question_id)["display_answer"],
        "knowledge_node_label": label,
        "written_prompt": (
            f"「{label}」について、選択肢や正答記号を使わず、"
            "判断の根拠となる中心概念を1〜2文で説明してくれ。"
        ),
        "rubric": {
            "pass_required_elements": [label, explanation],
            "partial_condition": "中心概念はあるが根拠・因果・条件が不足。",
            "fail_condition": "無関係、正答記号のみ、または中心概念が誤り。",
            "medical_critical_error": "正式解説の主要な因果・方向・適応を逆に説明。",
            "accepted_expression_guidance": "用語の完全一致ではなく、中心概念と因果の一致を見る。",
            "reference_explanation": explanation,
        },
        "formal_strong_alt_reference": True,
        "formal_repair_enabled_by_written": False,
    }


def _seven_cases(packet: dict[str, Any]) -> list[dict[str, str]]:
    return [
        {"kind": "clear_correct", "answer": packet["rubric"]["reference_explanation"], "expected": "PASS"},
        {"kind": "missing_required_element", "answer": packet["knowledge_node_label"], "expected": "PARTIAL"},
        {"kind": "plausible_wrong", "answer": "主要な因果関係は正式解説と逆である。", "expected": "FAIL"},
        {"kind": "memorized_answer", "answer": str(packet["source_display_answer"]), "expected": "FAIL"},
        {
            "kind": "critical_error",
            "answer": f"{packet['knowledge_node_label']}に関係するが、主要な方向と因果は正式解説の逆である。",
            "expected": "FAIL",
        },
        {"kind": "unrelated", "answer": "今日は天気が良い。", "expected": "FAIL"},
        {"kind": "empty", "answer": "", "expected": "UNKNOWN"},
    ]


def select_ai_shadow_representatives() -> list[dict[str, Any]]:
    artifact = build_shadow_review_artifact()
    written = artifact["singleton_written_review_packets"]
    chosen: list[dict[str, Any]] = []
    # 7 singleton representatives: critical, moderate, non-safety and broad fields.
    for safety in ("critical", "moderate", "none"):
        needed = {"critical": 2, "moderate": 2, "none": 3}[safety]
        for item in written:
            if item["safety"] == safety and item["field"] not in {x["field"] for x in chosen}:
                chosen.append({**item, "formal_strong_alt_reference": False})
                needed -= 1
                if needed == 0:
                    break
    audit = {item["canonical_node_id"]: item for item in build_repairability_audit()}
    for node_id in ("KN0268", "KN0652", "KN0899"):
        chosen.append(_strong_reference_packet(audit[node_id]))
    for item in chosen:
        item["cases"] = _seven_cases(item)
    return chosen


def fail_closed_evaluation(reason: str, target_node_id: str = "") -> dict[str, Any]:
    return {
        "target_node_id": target_node_id,
        "verdict": "UNKNOWN",
        "matched_required_elements": [],
        "missing_required_elements": [],
        "critical_error_detected": False,
        "short_reason": str(reason)[:300],
        "formal_state_change": False,
    }


def validate_structured_evaluation(
    payload: Any, target_node_id: str, rubric: dict[str, Any]
) -> dict[str, Any]:
    if not rubric or not rubric.get("pass_required_elements"):
        return fail_closed_evaluation("rubric missing", target_node_id)
    if not isinstance(payload, dict):
        return fail_closed_evaluation("malformed response", target_node_id)
    if str(payload.get("target_node_id")) != target_node_id:
        return fail_closed_evaluation("target Node mismatch", target_node_id)
    verdict = str(payload.get("verdict", "UNKNOWN")).upper()
    if verdict not in VERDICTS:
        return fail_closed_evaluation("invalid verdict", target_node_id)
    critical = payload.get("critical_error_detected") is True
    if critical and verdict == "PASS":
        verdict = "FAIL"
    matched = payload.get("matched_required_elements")
    missing = payload.get("missing_required_elements")
    if not isinstance(matched, list) or not isinstance(missing, list):
        return fail_closed_evaluation("invalid element lists", target_node_id)
    if verdict == "PASS" and missing:
        verdict = "PARTIAL"
    return {
        "target_node_id": target_node_id,
        "verdict": verdict,
        "matched_required_elements": [str(value)[:300] for value in matched],
        "missing_required_elements": [str(value)[:300] for value in missing],
        "critical_error_detected": critical,
        "short_reason": str(payload.get("short_reason", ""))[:300],
        "formal_state_change": False,
    }


def build_evaluator_messages(packet: dict[str, Any], answer: str) -> list[dict[str, str]]:
    contract = {
        "target_node_id": packet["canonical_node_id"],
        "written_prompt": packet["written_prompt"],
        "rubric": packet["rubric"],
        "learner_answer": answer,
        "required_output": {
            "target_node_id": packet["canonical_node_id"],
            "verdict": "PASS|PARTIAL|FAIL|UNKNOWN",
            "matched_required_elements": [],
            "missing_required_elements": [],
            "critical_error_detected": False,
            "short_reason": "",
        },
    }
    return [
        {
            "role": "system",
            "content": (
                "Node専用rubricのみで保守的に評価する。JSONのみ返す。"
                "必須要素不足はPASS禁止、医学的重大誤りはFAIL、判定不能はUNKNOWN。"
            ),
        },
        {"role": "user", "content": json.dumps(contract, ensure_ascii=False)},
    ]


def run_shadow_validation(
    evaluator: Callable[[dict[str, Any], str], Any], repeat_count: int = DEFAULT_REPEAT_COUNT
) -> dict[str, Any]:
    representatives = select_ai_shadow_representatives()
    rows = []
    api_calls = 0
    for packet in representatives:
        for case in packet["cases"]:
            evaluations = []
            for _ in range(repeat_count):
                if not case["answer"].strip():
                    evaluation = fail_closed_evaluation("empty answer", packet["canonical_node_id"])
                else:
                    api_calls += 1
                    try:
                        raw = evaluator(packet, case["answer"])
                        evaluation = validate_structured_evaluation(
                            raw, packet["canonical_node_id"], packet["rubric"]
                        )
                    except Exception:
                        evaluation = fail_closed_evaluation("API or parse failure", packet["canonical_node_id"])
                evaluations.append(evaluation)
            verdicts = [item["verdict"] for item in evaluations]
            rows.append({
                "canonical_node_id": packet["canonical_node_id"],
                "field": packet["field"],
                "safety": packet["safety"],
                "formal_strong_alt_reference": packet["formal_strong_alt_reference"],
                "case_kind": case["kind"],
                "expected": case["expected"],
                "verdicts": verdicts,
                "consistent": len(set(verdicts)) == 1,
                "false_pass": case["expected"] != "PASS" and "PASS" in verdicts,
                "false_fail_candidate": case["expected"] == "PASS" and any(v != "PASS" for v in verdicts),
                "formal_state_changes": sum(item["formal_state_change"] for item in evaluations),
            })
    correct_verdicts = [v for row in rows if row["expected"] == "PASS" for v in row["verdicts"]]
    return {
        "status": "completed",
        "model": DEFAULT_MODEL,
        "temperature": 0,
        "node_count": len(representatives),
        "case_count": len(rows),
        "repeat_count": repeat_count,
        "planned_api_calls": len(representatives) * 6 * repeat_count,
        "actual_api_calls": api_calls,
        "false_pass_count": sum(row["false_pass"] for row in rows),
        "false_fail_candidate_count": sum(row["false_fail_candidate"] for row in rows),
        "memorized_answer_pass_count": sum(
            row["case_kind"] == "memorized_answer" and "PASS" in row["verdicts"] for row in rows
        ),
        "critical_error_pass_count": sum(
            row["case_kind"] == "critical_error" and "PASS" in row["verdicts"] for row in rows
        ),
        "verdict_instability_count": sum(not row["consistent"] for row in rows),
        "pass_reproducibility": (
            sum(value == "PASS" for value in correct_verdicts) / len(correct_verdicts)
            if correct_verdicts else None
        ),
        "formal_state_changes": sum(row["formal_state_changes"] for row in rows),
        "rows": rows,
    }


def build_not_run_plan(status: str = "not_run_pending_explicit_api_authorization") -> dict[str, Any]:
    representatives = select_ai_shadow_representatives()
    return {
        "status": status,
        "model": DEFAULT_MODEL,
        "temperature": 0,
        "node_count": len(representatives),
        "case_count": len(representatives) * 7,
        "repeat_count": DEFAULT_REPEAT_COUNT,
        "planned_api_calls": len(representatives) * 6 * DEFAULT_REPEAT_COUNT,
        "actual_api_calls": 0,
        "false_pass_count": None,
        "false_fail_candidate_count": None,
        "verdict_instability_count": None,
        "pass_reproducibility": None,
        "formal_state_changes": 0,
        "representatives": [
            {
                "canonical_node_id": item["canonical_node_id"],
                "field": item["field"],
                "safety": item["safety"],
                "formal_strong_alt_reference": item["formal_strong_alt_reference"],
            }
            for item in representatives
        ],
    }
