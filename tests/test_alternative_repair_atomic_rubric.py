from alternative_repair_atomic_rubric import (
    apply_strict_pass_gate,
    build_atomic_plan,
    build_atomic_rubric,
    fail_closed_atomic,
    run_atomic_shadow,
    select_atomic_shadow_representatives,
)


def _payload(packet, matched, *, ai="PASS", critical=False, target=None):
    required = {item["id"] for item in packet["atomic_rubric"]["required_elements"]}
    matched = set(matched)
    return {
        "target_node_id": target or packet["canonical_node_id"],
        "ai_verdict": ai,
        "matched_required_element_ids": sorted(matched),
        "missing_required_element_ids": sorted(required - matched),
        "critical_error_detected": critical,
        "critical_error_reason": "reverse" if critical else "",
        "short_reason": "test",
    }


def test_all_10_rubrics_have_two_to_four_unique_atomic_elements():
    packets = select_atomic_shadow_representatives()
    assert len(packets) == 10
    for packet in packets:
        required = packet["atomic_rubric"]["required_elements"]
        assert 2 <= len(required) <= 4
        assert len({item["id"] for item in required}) == len(required)
        assert all(item["criterion"] for item in required)


def test_all_elements_and_no_error_is_only_pass_path():
    packet = select_atomic_shadow_representatives()[0]
    ids = {item["id"] for item in packet["atomic_rubric"]["required_elements"]}
    result = apply_strict_pass_gate(_payload(packet, ids), packet["canonical_node_id"], packet["atomic_rubric"])
    assert result["final_shadow_verdict"] == "PASS"
    assert not result["formal_state_change"]


def test_one_or_multiple_missing_elements_cannot_pass_even_if_ai_passes():
    packet = select_atomic_shadow_representatives()[0]
    ids = [item["id"] for item in packet["atomic_rubric"]["required_elements"]]
    one_missing = apply_strict_pass_gate(_payload(packet, ids[:-1]), packet["canonical_node_id"], packet["atomic_rubric"])
    none = apply_strict_pass_gate(_payload(packet, []), packet["canonical_node_id"], packet["atomic_rubric"])
    assert one_missing["ai_verdict"] == "PASS" and one_missing["final_shadow_verdict"] == "PARTIAL"
    assert none["final_shadow_verdict"] == "FAIL"


def test_node_label_only_and_kn0899_regression_are_non_pass():
    packet = next(item for item in select_atomic_shadow_representatives() if item["canonical_node_id"] == "KN0899")
    first = packet["atomic_rubric"]["required_elements"][0]["id"]
    result = apply_strict_pass_gate(_payload(packet, [first]), "KN0899", packet["atomic_rubric"])
    assert result["ai_verdict"] == "PASS"
    assert result["final_shadow_verdict"] == "PARTIAL"
    assert "missing_required_elements" in result["gate_blocks"]


def test_critical_error_blocks_pass_with_all_elements():
    packet = select_atomic_shadow_representatives()[0]
    ids = {item["id"] for item in packet["atomic_rubric"]["required_elements"]}
    result = apply_strict_pass_gate(_payload(packet, ids, critical=True), packet["canonical_node_id"], packet["atomic_rubric"])
    assert result["final_shadow_verdict"] == "FAIL"


def test_synonymous_wording_is_an_explicit_rubric_instruction():
    rubric = build_atomic_rubric(select_atomic_shadow_representatives()[0])
    assert all("同義" in item["acceptable_wording"] for item in rubric["required_elements"])


def test_target_mismatch_malformed_and_api_error_fail_closed():
    packet = select_atomic_shadow_representatives()[0]
    ids = {item["id"] for item in packet["atomic_rubric"]["required_elements"]}
    mismatch = apply_strict_pass_gate(_payload(packet, ids, target="KN9999"), packet["canonical_node_id"], packet["atomic_rubric"])
    malformed = apply_strict_pass_gate("bad", packet["canonical_node_id"], packet["atomic_rubric"])
    api_error = fail_closed_atomic("api error", packet["canonical_node_id"])
    assert {mismatch["final_shadow_verdict"], malformed["final_shadow_verdict"], api_error["final_shadow_verdict"]} == {"UNKNOWN"}


def test_shadow_runner_detects_ai_pass_gate_blocks_without_state_mutation():
    def evaluator(packet, answer):
        first = packet["atomic_rubric"]["required_elements"][0]["id"]
        return _payload(packet, [first], ai="PASS")
    report = run_atomic_shadow(evaluator, repeat_count=1)
    assert report["ai_pass_gate_block_count"] > 0
    assert report["formal_state_changes"] == 0
    assert report["actual_api_calls"] == 70


def test_deterministic_10_by_8_suite_has_zero_final_false_pass():
    def evaluator(packet, answer):
        case = next(item for item in packet["cases"] if item["answer"] == answer)
        ids = [item["id"] for item in packet["atomic_rubric"]["required_elements"]]
        if case["kind"] == "clear_correct":
            return _payload(packet, ids, ai="PASS")
        if case["kind"] in {"missing_required_element", "adversarial_label_only"}:
            return _payload(packet, ids[:1], ai="PASS")
        if case["kind"] == "critical_error":
            return _payload(packet, ids, ai="PASS", critical=True)
        return _payload(packet, [], ai="FAIL")

    report = run_atomic_shadow(evaluator, repeat_count=1)
    assert report["case_count"] == 80
    assert report["adversarial_case_count"] == 10
    assert report["false_pass_count"] == 0
    assert report["memorized_answer_pass_count"] == 0
    assert report["critical_error_pass_count"] == 0
    assert report["unrelated_pass_count"] == 0
    assert report["kn0899_recurrence_count"] == 0
    assert report["formal_state_changes"] == 0


def test_plan_has_10_adversarial_cases_and_140_calls():
    plan = build_atomic_plan()
    assert plan["node_count"] == 10
    assert plan["case_count"] == 80
    assert plan["adversarial_case_count"] == 10
    assert plan["repeat_count"] == 2
    assert plan["planned_api_calls"] == 140
    assert plan["formal_state_changes"] == 0
