from collections import Counter

from alternative_repair_confirmation_shadow import (
    build_relation_review_packets,
    build_shadow_review_artifact,
    build_written_review_packets,
    evaluate_deterministic_shadow_case,
    fail_closed_shadow_evaluation,
)


def test_relation_review_has_exactly_11_source_nodes_and_never_auto_accepts():
    packets = build_relation_review_packets()
    assert len(packets) == 11
    assert {item["recommended_decision"] for item in packets} == {"UNCERTAIN"}
    assert all(not item["formal_repair_enabled"] for item in packets)
    assert sum(
        len(item["candidate_confirmations"]) for item in packets
    ) == 13


def test_singleton_sample_has_30_nodes_and_all_18_fields():
    packets = build_written_review_packets()
    assert len(packets) == 30
    assert len({item["canonical_node_id"] for item in packets}) == 30
    assert len({item["field"] for item in packets}) == 18
    assert all(not item["formal_repair_enabled"] for item in packets)


def test_each_written_check_has_a_node_specific_rubric_and_six_cases():
    packets = build_written_review_packets()
    assert all(item["knowledge_node_label"] in item["rubric"]["pass_required_elements"] for item in packets)
    assert all(item["rubric"]["reference_explanation"] for item in packets)
    assert all(len(item["deterministic_cases"]) == 6 for item in packets)


def test_deterministic_false_pass_suite_is_fail_closed():
    results = Counter()
    false_pass = 0
    memorized_pass = 0
    for packet in build_written_review_packets():
        for case in packet["deterministic_cases"]:
            outcome = evaluate_deterministic_shadow_case(packet, case)
            assert outcome["shadow_result"] == case["expected"]
            results[outcome["shadow_result"]] += 1
            assert not outcome["formal_state_change"]
            assert outcome["remain_repairing"]
            false_pass += case["kind"] != "clear_correct" and outcome["shadow_result"] == "PASS"
            memorized_pass += case["kind"] == "memorized_choice_only" and outcome["shadow_result"] == "PASS"
    assert results == {"PASS": 30, "PARTIAL": 30, "FAIL": 90, "UNKNOWN": 30}
    assert false_pass == 0
    assert memorized_pass == 0


def test_partial_fail_unknown_and_api_error_never_change_formal_state():
    for result in ("PARTIAL", "FAIL", "UNKNOWN", "API_ERROR"):
        outcome = fail_closed_shadow_evaluation(result)
        assert outcome["remain_repairing"]
        assert not outcome["formal_state_change"]


def test_strong_reference_nodes_are_exact_and_written_not_assumed_equivalent():
    references = build_shadow_review_artifact()["strong_alt_reference_nodes"]
    assert {item["canonical_node_id"] for item in references} == {
        "KN0268", "KN0652", "KN0899"
    }
    assert all(item["written_is_not_assumed_equivalent"] for item in references)


def test_artifact_declares_zero_state_adaptive_db_and_api_effects():
    safety = build_shadow_review_artifact()["safety"]
    assert safety == {
        "formal_state_changes": 0,
        "adaptive_changes": 0,
        "database_writes": 0,
        "production_api_calls": 0,
    }
