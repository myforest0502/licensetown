from copy import deepcopy

import pytest

import dashboard_real_data_shadow as shadow


STATE_COUNTS = {
    "unseen": 9,
    "repairing": 0,
    "checking": 1,
    "recheck_due": 0,
    "repaired": 0,
    "stable": 0,
}


def fake_inputs():
    fields = []
    progress_fields = []
    profiles = {}
    for field_id in range(1, 19):
        name = f"F{field_id}"
        fields.append({
            "field_id": field_id,
            "field_name": name,
            "total_canonical_node_count": 10,
            "evaluable_answer_count": 1,
            "question_answer_count": 1,
            "question_accuracy": 1.0,
            "evaluable_accuracy": 1.0,
        })
        progress_fields.append({
            "field_id": field_id,
            "field_name": name,
            "total_canonical_nodes": 10,
            "touched_canonical_nodes": 1,
            "node_coverage": 0.1,
            "state_score_sum": 0.3,
            "state_mastery": 0.3,
            "progress_score": 0.03,
            "field_progress_score": 0.03,
            "field_progress_percent": 3.0,
            "state_counts": deepcopy(STATE_COUNTS),
        })
        profiles[name] = {
            "field_id": field_id,
            "field_name": name,
            "critical_safety_unresolved_count": 0,
            "active_cross_question_confident_wrong_node_count": 0,
            "active_confident_wrong_repairing_node_count": 0,
            "active_cross_question_wrong_node_count": 0,
            "active_repeated_weakness_node_count": 0,
            "active_evaluable_wrong_repairing_node_count": 0,
            "recheck_due_node_count": 0,
        }
    evidence = {
        "status": "evidence_only",
        "fields": fields,
    }
    progress = {
        "status": "field_progress_v0.1_shadow",
        "fields": progress_fields,
        "overall": {
            "total_unique_canonical_nodes": 180,
            "touched_unique_canonical_nodes": 18,
            "state_counts": deepcopy(STATE_COUNTS),
            "state_score_sum": 5.4,
            "overall_progress_score": 0.03,
            "overall_progress_percent": 3.0,
        },
    }
    return evidence, progress, profiles


def build(monkeypatch, evidence, progress, profiles, attempts=None, **kwargs):
    monkeypatch.setattr(
        shadow,
        "build_field_judgment_evidence_profiles",
        lambda attempts, evidence, as_of=None: profiles,
    )
    return shadow.build_dashboard_real_data_shadow(
        attempts or [], evidence=evidence, progress=progress, **kwargs
    )


def test_empty_or_sparse_history_is_coverage_priority_not_proven_weakness(monkeypatch):
    evidence, progress, profiles = fake_inputs()
    result = build(monkeypatch, evidence, progress, profiles)
    assert result["field_count"] == 18
    assert len(result["weakness_top3"]) == 3
    assert all(item["reason_code"] == "coverage_expand" for item in result["weakness_top3"])
    assert all(item["is_proven_weakness"] is False for item in result["weakness_top3"])
    assert result["recommendation_intent"]["learning_intent"] == "exploration"
    assert result["recommendation_intent"]["exact_question_ids"] is None
    assert result["exact_question_selection_performed"] is False


def test_critical_safety_outranks_confident_wrong_and_recheck(monkeypatch):
    evidence, progress, profiles = fake_inputs()
    profiles["F8"]["critical_safety_unresolved_count"] = 1
    profiles["F2"]["active_cross_question_confident_wrong_node_count"] = 3
    profiles["F3"]["recheck_due_node_count"] = 4
    result = build(monkeypatch, evidence, progress, profiles)
    assert [item["reason_code"] for item in result["weakness_top3"][:3]] == [
        "safety_repair", "confident_wrong_repair", "retention_recheck"
    ]
    assert result["weakness_top3"][0]["field_id"] == 8
    assert result["recommendation_intent"]["safety_priority"] is True
    assert result["advice"]["intent"] == "safety_repair"


def test_repeated_wrong_outranks_plain_repairing(monkeypatch):
    evidence, progress, profiles = fake_inputs()
    profiles["F5"]["active_repeated_weakness_node_count"] = 2
    profiles["F4"]["active_evaluable_wrong_repairing_node_count"] = 5
    result = build(monkeypatch, evidence, progress, profiles)
    assert result["weakness_top3"][0]["field_id"] == 5
    assert result["weakness_top3"][0]["reason_code"] == "repeated_wrong_repair"
    assert result["weakness_top3"][1]["reason_code"] == "repairing_continue"


def test_high_accuracy_low_coverage_remains_coverage_when_sample_is_small(monkeypatch):
    evidence, progress, profiles = fake_inputs()
    evidence["fields"][0]["question_accuracy"] = 1.0
    evidence["fields"][0]["evaluable_accuracy"] = 1.0
    evidence["fields"][0]["evaluable_answer_count"] = 3
    result = build(monkeypatch, evidence, progress, profiles)
    first = next(item for item in result["weakness_top3"] if item["field_id"] == 1)
    assert first["reason_code"] == "coverage_expand"
    assert first["is_proven_weakness"] is False


def test_material_low_progress_requires_reliable_evaluable_sample(monkeypatch):
    evidence, progress, profiles = fake_inputs()
    evidence["fields"][6]["evaluable_answer_count"] = 10
    progress["fields"][6]["field_progress_score"] = 0.20
    progress["fields"][6]["field_progress_percent"] = 20.0
    result = build(monkeypatch, evidence, progress, profiles)
    assert result["weakness_top3"][0]["field_id"] == 7
    assert result["weakness_top3"][0]["reason_code"] == "low_progress_repair"
    assert result["weakness_top3"][0]["is_proven_weakness"] is True


def test_comparison_never_averages_legacy_and_shadow_values(monkeypatch):
    evidence, progress, profiles = fake_inputs()
    result = build(
        monkeypatch,
        evidence,
        progress,
        profiles,
        legacy_overall_progress_percent=80,
        legacy_weak_fields=["旧弱点"],
        legacy_recommended_field="F2",
    )
    assert result["overall"]["overall_progress_percent"] == 3.0
    assert result["comparison"]["legacy_overall_progress_percent"] == 80
    assert result["comparison"]["shadow_overall_progress_percent"] == 3.0
    assert result["authoritative_attempt_source"] == "question_attempts"
    assert result["authoritative_node_state_source"] == "pure_derive_all_user_node_states"
    assert result["phase11_promoted"] is False


def test_invalid_missing_field_progress_is_not_silently_filled(monkeypatch):
    evidence, progress, profiles = fake_inputs()
    progress["fields"].pop()
    monkeypatch.setattr(
        shadow,
        "build_field_judgment_evidence_profiles",
        lambda attempts, evidence, as_of=None: profiles,
    )
    with pytest.raises(KeyError):
        shadow.build_dashboard_real_data_shadow([], evidence=evidence, progress=progress)
