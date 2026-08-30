"""Atomic rubrics and an application-side strict PASS gate (shadow only)."""

from __future__ import annotations

import json
import re
from typing import Any, Callable

from alternative_repair_ai_reliability import (
    DEFAULT_MODEL,
    select_ai_shadow_representatives,
)


VERDICTS = {"PASS", "PARTIAL", "FAIL", "UNKNOWN"}
REPEAT_COUNT = 2


def _atomic_clauses(label: str, reference: str) -> list[str]:
    """Create 2-4 reviewable semantic clauses without changing formal content."""
    cleaned = re.sub(r"\d+が正しい。?$", "", str(reference)).strip()
    source = str(label).strip() or cleaned
    parts = [
        part.strip("、。 ")
        for part in re.split(r"、|(?<=する)と|(?<=で)、", source)
        if part.strip("、。 ")
    ]
    if len(parts) < 2:
        parts.extend(
            part.strip("、。 ")
            for part in re.split(r"。", cleaned)
            if part.strip("、。 ") and part.strip("、。 ") not in parts
        )
    if len(parts) < 2:
        parts = [source, f"その知識を判断根拠として説明できる: {cleaned}"]
    return parts[:4]


def build_atomic_rubric(packet: dict[str, Any]) -> dict[str, Any]:
    clauses = _atomic_clauses(
        packet["knowledge_node_label"], packet["rubric"]["reference_explanation"]
    )
    required = [
        {
            "id": f"R{index}",
            "criterion": clause,
            "acceptable_wording": "医学的に同義な用語・略語・語順違いを許容する。",
        }
        for index, clause in enumerate(clauses, start=1)
    ]
    return {
        "version": "0.2-atomic",
        "required_elements": required,
        "partial_condition": "必須elementを1つ以上満たすが全数ではない。",
        "fail_condition": "必須elementを1つも満たさない、無関係、または暗記記号のみ。",
        "critical_errors": [
            "主要な因果関係・方向・適応・禁忌を逆に説明する。"
        ],
        "memorized_answer_rejection": (
            "Node名、疾患名、用語名、または元問題の正答記号だけではPASS不可。"
        ),
        "reference_explanation": packet["rubric"]["reference_explanation"],
    }


def select_atomic_shadow_representatives() -> list[dict[str, Any]]:
    items = []
    for source in select_ai_shadow_representatives():
        packet = {**source, "atomic_rubric": build_atomic_rubric(source)}
        packet["cases"] = [*source["cases"], {
            "kind": "adversarial_label_only",
            "answer": source["knowledge_node_label"],
            "expected": "PARTIAL",
        }]
        items.append(packet)
    return items


def fail_closed_atomic(reason: str, target_node_id: str = "") -> dict[str, Any]:
    return {
        "target_node_id": target_node_id,
        "ai_verdict": "UNKNOWN",
        "final_shadow_verdict": "UNKNOWN",
        "matched_required_element_ids": [],
        "missing_required_element_ids": [],
        "critical_error_detected": False,
        "critical_error_reason": "",
        "short_reason": str(reason)[:300],
        "gate_blocks": ["parse_or_contract_error"],
        "formal_state_change": False,
    }


def apply_strict_pass_gate(
    payload: Any, target_node_id: str, rubric: dict[str, Any]
) -> dict[str, Any]:
    required_items = rubric.get("required_elements") if isinstance(rubric, dict) else None
    if not isinstance(required_items, list) or not (2 <= len(required_items) <= 4):
        return fail_closed_atomic("atomic rubric incomplete", target_node_id)
    required_ids = {str(item.get("id")) for item in required_items if item.get("id")}
    if len(required_ids) != len(required_items) or not isinstance(payload, dict):
        return fail_closed_atomic("rubric or response malformed", target_node_id)
    if str(payload.get("target_node_id")) != target_node_id:
        result = fail_closed_atomic("target Node mismatch", target_node_id)
        result["gate_blocks"] = ["target_mismatch"]
        return result
    ai_verdict = str(payload.get("ai_verdict", "UNKNOWN")).upper()
    if ai_verdict not in VERDICTS:
        return fail_closed_atomic("invalid AI verdict", target_node_id)
    matched = payload.get("matched_required_element_ids")
    missing_reported = payload.get("missing_required_element_ids")
    if not isinstance(matched, list) or not isinstance(missing_reported, list):
        return fail_closed_atomic("element IDs malformed", target_node_id)
    matched_ids = {str(value) for value in matched} & required_ids
    missing_ids = required_ids - matched_ids
    critical = payload.get("critical_error_detected") is True
    blocks = []
    if missing_ids:
        blocks.append("missing_required_elements")
    if critical:
        blocks.append("critical_error")
    if critical:
        final = "FAIL"
    elif matched_ids == required_ids:
        final = "PASS"
    elif matched_ids:
        final = "PARTIAL"
    else:
        final = "FAIL"
    return {
        "target_node_id": target_node_id,
        "ai_verdict": ai_verdict,
        "final_shadow_verdict": final,
        "matched_required_element_ids": sorted(matched_ids),
        "missing_required_element_ids": sorted(missing_ids),
        "critical_error_detected": critical,
        "critical_error_reason": str(payload.get("critical_error_reason", ""))[:300],
        "short_reason": str(payload.get("short_reason", ""))[:300],
        "gate_blocks": blocks,
        "formal_state_change": False,
    }


def build_atomic_evaluator_messages(packet: dict[str, Any], answer: str) -> list[dict[str, str]]:
    contract = {
        "target_node_id": packet["canonical_node_id"],
        "written_prompt": packet["written_prompt"],
        "atomic_rubric": packet["atomic_rubric"],
        "learner_answer": answer,
        "required_output": {
            "target_node_id": packet["canonical_node_id"],
            "ai_verdict": "PASS|PARTIAL|FAIL|UNKNOWN",
            "matched_required_element_ids": [],
            "missing_required_element_ids": [],
            "critical_error_detected": False,
            "critical_error_reason": "",
            "short_reason": "",
        },
    }
    return [
        {
            "role": "system",
            "content": (
                "各atomic required elementを独立に判定しJSONのみ返す。"
                "Node名や正答記号だけでelementをmatchedにしない。"
                "重大な因果・方向・適応の逆転はcritical errorとする。"
                "AI verdictは参考であり、最終PASSは外側gateが決める。"
            ),
        },
        {"role": "user", "content": json.dumps(contract, ensure_ascii=False)},
    ]


def run_atomic_shadow(
    evaluator: Callable[[dict[str, Any], str], Any], repeat_count: int = REPEAT_COUNT
) -> dict[str, Any]:
    packets = select_atomic_shadow_representatives()
    rows = []
    actual_calls = 0
    api_errors = 0
    for packet in packets:
        for case in packet["cases"]:
            evaluations = []
            for _ in range(repeat_count):
                if not case["answer"].strip():
                    result = fail_closed_atomic("empty answer", packet["canonical_node_id"])
                else:
                    actual_calls += 1
                    try:
                        payload = evaluator(packet, case["answer"])
                        result = apply_strict_pass_gate(
                            payload, packet["canonical_node_id"], packet["atomic_rubric"]
                        )
                    except Exception:
                        api_errors += 1
                        result = fail_closed_atomic("API or parse failure", packet["canonical_node_id"])
                evaluations.append(result)
            ai_verdicts = [item["ai_verdict"] for item in evaluations]
            finals = [item["final_shadow_verdict"] for item in evaluations]
            expected = case["expected"]
            rows.append({
                "canonical_node_id": packet["canonical_node_id"],
                "case_kind": case["kind"],
                "expected": expected,
                "ai_verdicts": ai_verdicts,
                "final_shadow_verdicts": finals,
                "consistent": len(set(finals)) == 1,
                "ai_pass_gate_block_count": sum(
                    item["ai_verdict"] == "PASS" and item["final_shadow_verdict"] != "PASS"
                    for item in evaluations
                ),
                "missing_element_block_count": sum(
                    "missing_required_elements" in item["gate_blocks"] for item in evaluations
                ),
                "critical_error_block_count": sum(
                    "critical_error" in item["gate_blocks"] for item in evaluations
                ),
                "target_mismatch_block_count": sum(
                    "target_mismatch" in item["gate_blocks"] for item in evaluations
                ),
                "parse_error_block_count": sum(
                    "parse_or_contract_error" in item["gate_blocks"] for item in evaluations
                ),
                "false_pass": expected != "PASS" and "PASS" in finals,
                "false_fail_candidate": expected == "PASS" and any(value != "PASS" for value in finals),
                "formal_state_changes": sum(item["formal_state_change"] for item in evaluations),
            })
    correct = [value for row in rows if row["expected"] == "PASS" for value in row["final_shadow_verdicts"]]
    return {
        "status": "completed",
        "model": DEFAULT_MODEL,
        "temperature": 0,
        "node_count": len(packets),
        "average_required_element_count": sum(len(item["atomic_rubric"]["required_elements"]) for item in packets) / len(packets),
        "case_count": len(rows),
        "adversarial_case_count": len(packets),
        "repeat_count": repeat_count,
        "planned_api_calls": len(packets) * 7 * repeat_count,
        "actual_api_calls": actual_calls,
        "api_error_count": api_errors,
        "ai_pass_count": sum(value == "PASS" for row in rows for value in row["ai_verdicts"]),
        "final_pass_count": sum(value == "PASS" for row in rows for value in row["final_shadow_verdicts"]),
        "ai_pass_gate_block_count": sum(row["ai_pass_gate_block_count"] for row in rows),
        "false_pass_count": sum(row["false_pass"] for row in rows),
        "false_fail_candidate_count": sum(row["false_fail_candidate"] for row in rows),
        "memorized_answer_pass_count": sum(row["case_kind"] == "memorized_answer" and "PASS" in row["final_shadow_verdicts"] for row in rows),
        "critical_error_pass_count": sum(row["case_kind"] == "critical_error" and "PASS" in row["final_shadow_verdicts"] for row in rows),
        "unrelated_pass_count": sum(row["case_kind"] == "unrelated" and "PASS" in row["final_shadow_verdicts"] for row in rows),
        "adversarial_pass_count": sum(row["case_kind"] == "adversarial_label_only" and "PASS" in row["final_shadow_verdicts"] for row in rows),
        "kn0899_recurrence_count": sum(row["canonical_node_id"] == "KN0899" and row["case_kind"] in {"missing_required_element", "adversarial_label_only"} and "PASS" in row["final_shadow_verdicts"] for row in rows),
        "verdict_instability_count": sum(not row["consistent"] for row in rows),
        "pass_reproducibility": sum(value == "PASS" for value in correct) / len(correct) if correct else None,
        "missing_element_block_count": sum(row["missing_element_block_count"] for row in rows),
        "critical_error_block_count": sum(row["critical_error_block_count"] for row in rows),
        "target_mismatch_block_count": sum(row["target_mismatch_block_count"] for row in rows),
        "parse_error_block_count": sum(row["parse_error_block_count"] for row in rows),
        "fail_closed_count": sum(row["parse_error_block_count"] for row in rows) + len(packets) * repeat_count,
        "formal_state_changes": sum(row["formal_state_changes"] for row in rows),
        "rows": rows,
    }


def build_atomic_plan() -> dict[str, Any]:
    packets = select_atomic_shadow_representatives()
    return {
        "status": "not_run_pending_explicit_api_authorization",
        "node_count": 10,
        "average_required_element_count": sum(len(item["atomic_rubric"]["required_elements"]) for item in packets) / 10,
        "case_count": 80,
        "adversarial_case_count": 10,
        "repeat_count": 2,
        "planned_api_calls": 140,
        "actual_api_calls": 0,
        "formal_state_changes": 0,
        "rubrics": [
            {"canonical_node_id": item["canonical_node_id"], "atomic_rubric": item["atomic_rubric"]}
            for item in packets
        ],
    }
