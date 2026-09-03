from knowledge_node_repairability import (
    SAME_QUESTION_ONLY,
    STRONG_ALT,
    WEAK_ALT_ONLY,
    build_repairability_audit,
    shadow_confirmation_outcome,
    summarize_repairability,
)


def test_all_1508_canonical_nodes_are_classified_and_counts_balance():
    records = build_repairability_audit()
    summary = summarize_repairability(records)
    assert summary["canonical_node_count"] == 1508
    assert summary["singleton_node_count"] == 1342
    assert summary["multi_question_node_count"] == 166
    assert summary["singleton_node_count"] + summary["multi_question_node_count"] == 1508
    assert summary["strong_alt_question_available_node_count"] == 112
    assert summary["weak_alt_question_only_node_count"] == 54


def test_multi_question_classification_uses_formal_evidence_not_question_count_only():
    records = build_repairability_audit()
    strong = [item for item in records if item["classification"] == STRONG_ALT]
    weak = [item for item in records if item["classification"] == WEAK_ALT_ONLY]
    assert strong and weak
    assert all(item["strong_alt_pairs"] for item in strong)
    assert all(not item["strong_alt_pairs"] and item["weak_alt_pairs"] for item in weak)


def test_singleton_same_question_only_is_not_formally_repairable():
    item = next(
        item for item in build_repairability_audit()
        if item["question_count"] == 1 and not item["relation_candidates"]
    )
    assert item["classification"] == SAME_QUESTION_ONLY
    assert not item["repairable"]
    assert item["currently_unrepairable"]
    assert "same_question_fallback" in item["confirmation_path"]
    assert item["formal_confirmation_candidate_count"] == 0


def test_relations_are_candidates_only_and_never_implicitly_enabled():
    related = [item for item in build_repairability_audit() if item["relation_candidates"]]
    assert related
    assert all(
        not candidate["formally_enabled_for_repair"]
        for item in related for candidate in item["relation_candidates"]
    )


def test_case_a_existing_strong_path_is_eligible_only_as_shadow_candidate():
    result = shadow_confirmation_outcome("strong_alt_question", "PASS")
    assert result["repair_candidate"]
    assert result["formal_state_change"] is False


def test_cases_b_c_weak_and_same_question_remain_repairing():
    for path in ("weak_alt_question", "same_question"):
        result = shadow_confirmation_outcome(path, "PASS")
        assert result["remain_repairing"]
        assert not result["formal_state_change"]


def test_case_d_validated_relation_is_still_candidate_before_formal_adoption():
    result = shadow_confirmation_outcome("validated_transfer", "PASS")
    assert result["remain_repairing"]
    assert not result["repair_candidate"]


def test_cases_e_f_written_pass_and_all_fail_closed_results_do_not_change_state():
    for result_name in ("PASS", "PARTIAL", "FAIL", "UNKNOWN", "API_ERROR"):
        result = shadow_confirmation_outcome("written_confirmation", result_name)
        assert result["remain_repairing"]
        assert not result["formal_state_change"]


def test_safety_nodes_follow_the_same_conservative_rules():
    safety_nodes = [
        item for item in build_repairability_audit()
        if any(value in {"moderate", "critical"} for value in item["safety"])
    ]
    assert safety_nodes
    assert all(item["repairable"] == bool(item["strong_alt_pairs"]) for item in safety_nodes)


def test_audit_script_contains_no_write_sql_or_user_identifier_output():
    from pathlib import Path

    source = (Path(__file__).parents[1] / "scripts" / "audit_singleton_repairability.py").read_text(
        encoding="utf-8"
    ).upper()
    for token in ("INSERT ", "UPDATE ", "DELETE ", "TRUNCATE ", "ALTER TABLE", "CREATE TABLE"):
        assert token not in source
    assert '"USER_ID":' not in source
