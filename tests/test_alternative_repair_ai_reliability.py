import json

from alternative_repair_ai_reliability import (
    build_evaluator_messages,
    build_not_run_plan,
    fail_closed_evaluation,
    run_shadow_validation,
    select_ai_shadow_representatives,
    validate_structured_evaluation,
)


def _valid(packet, verdict="PASS", *, critical=False, target=None, missing=None):
    return {
        "target_node_id": target or packet["canonical_node_id"],
        "verdict": verdict,
        "matched_required_elements": ["core"],
        "missing_required_elements": list(missing or []),
        "critical_error_detected": critical,
        "short_reason": "reason",
    }


def test_representative_set_is_10_with_safety_and_three_strong_references():
    items = select_ai_shadow_representatives()
    assert len(items) == 10
    assert {item["safety"] for item in items} >= {"critical", "moderate", "none"}
    assert sum(item["formal_strong_alt_reference"] for item in items) == 3
    assert all(len(item["cases"]) == 7 for item in items)


def test_structured_pass_partial_fail_unknown_are_accepted_shadow_only():
    packet = select_ai_shadow_representatives()[0]
    for verdict in ("PASS", "PARTIAL", "FAIL", "UNKNOWN"):
        result = validate_structured_evaluation(_valid(packet, verdict), packet["canonical_node_id"], packet["rubric"])
        assert result["verdict"] == verdict
        assert not result["formal_state_change"]


def test_critical_error_and_missing_element_cannot_pass():
    packet = select_ai_shadow_representatives()[0]
    critical = validate_structured_evaluation(_valid(packet, critical=True), packet["canonical_node_id"], packet["rubric"])
    missing = validate_structured_evaluation(_valid(packet, missing=["required"]), packet["canonical_node_id"], packet["rubric"])
    assert critical["verdict"] == "FAIL"
    assert missing["verdict"] == "PARTIAL"


def test_malformed_target_mismatch_and_missing_rubric_fail_closed():
    packet = select_ai_shadow_representatives()[0]
    assert validate_structured_evaluation("bad", packet["canonical_node_id"], packet["rubric"])["verdict"] == "UNKNOWN"
    assert validate_structured_evaluation(_valid(packet, target="KN9999"), packet["canonical_node_id"], packet["rubric"])["verdict"] == "UNKNOWN"
    assert validate_structured_evaluation(_valid(packet), packet["canonical_node_id"], {})["verdict"] == "UNKNOWN"


def test_prompt_contains_node_rubric_and_structured_contract():
    packet = select_ai_shadow_representatives()[0]
    messages = build_evaluator_messages(packet, "answer")
    body = json.loads(messages[1]["content"])
    assert body["target_node_id"] == packet["canonical_node_id"]
    assert body["rubric"] == packet["rubric"]
    assert body["required_output"]["verdict"] == "PASS|PARTIAL|FAIL|UNKNOWN"


def test_api_error_empty_and_memorized_answer_never_mutate_state_or_false_pass():
    def evaluator(packet, answer):
        if answer == packet["source_display_answer"]:
            return _valid(packet, "FAIL")
        raise RuntimeError("offline")

    report = run_shadow_validation(evaluator, repeat_count=1)
    assert report["formal_state_changes"] == 0
    assert report["memorized_answer_pass_count"] == 0
    assert report["actual_api_calls"] == 60


def test_repeatability_metrics_detect_instability_and_false_pass():
    calls = {}
    def evaluator(packet, answer):
        key = (packet["canonical_node_id"], answer)
        calls[key] = calls.get(key, 0) + 1
        verdict = "PASS" if calls[key] == 2 else "FAIL"
        return _valid(packet, verdict)

    report = run_shadow_validation(evaluator, repeat_count=3)
    assert report["verdict_instability_count"] > 0
    assert report["false_pass_count"] > 0
    assert report["formal_state_changes"] == 0


def test_plan_has_70_cases_120_calls_and_zero_actual_calls():
    plan = build_not_run_plan()
    assert plan["node_count"] == 10
    assert plan["case_count"] == 70
    assert plan["repeat_count"] == 2
    assert plan["planned_api_calls"] == 120
    assert plan["actual_api_calls"] == 0
    assert plan["formal_state_changes"] == 0


def test_fail_closed_never_changes_formal_state():
    result = fail_closed_evaluation("timeout", "KN0001")
    assert result["verdict"] == "UNKNOWN"
    assert not result["formal_state_change"]
