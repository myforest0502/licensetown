from datetime import datetime, timedelta, timezone

import judgment_shadow
from judgment_shadow import (
    build_field_judgment_evidence_profiles,
    build_shadow_comparison,
    build_shadow_judgment,
)


NOW = datetime(2026, 9, 1, 9, 0, tzinfo=timezone.utc)


def attempt(q, node, *, correct, confidence=None, days=0, user="u", unknown=False):
    return {
        "user_id": user,
        "question_id": q,
        "knowledge_node_id": node,
        "is_correct": correct,
        "confidence": confidence,
        "answer_status": "unknown" if unknown else "answered",
        "selected_answers": [] if unknown else ["1"],
        "answered_at": NOW - timedelta(days=days),
        "event_key": f"{q}-{node}-{days}-{confidence}-{correct}",
        "attempt_position": 1,
    }


def evidence(*, states=None, overrides=None):
    states = states or {}
    overrides = overrides or {}
    fields = []
    for field_id in range(1, 19):
        base = {
            "field_id": field_id,
            "field_name": f"F{field_id}",
            "question_answer_count": 10,
            "question_accuracy": 0.8,
            "repairing_node_count": 0,
            "checking_node_count": 0,
            "recheck_due_node_count": 0,
            "retention_nodes": [],
            "node_coverage": {"percent": 20.0},
        }
        base.update(overrides.get(field_id, {}))
        fields.append(base)
    return {
        "fields": fields,
        "canonical_node_evidence": [
            {
                "canonical_node_id": node,
                "state": value if isinstance(value, str) else value.get("state"),
                "due_overdue_days": 0 if isinstance(value, str) else value.get("due_overdue_days", 0),
            }
            for node, value in states.items()
        ],
    }


def catalog(monkeypatch, mapping, *, critical=()):
    field_by_question = {q: field for q, (node, field) in mapping.items()}
    node_by_question = {q: node for q, (node, field) in mapping.items()}
    fields_by_node = {}
    for q, (node, field) in mapping.items():
        fields_by_node.setdefault(node, set()).add(field)
    monkeypatch.setattr(judgment_shadow, "_CATALOG", {
        "field_by_question": field_by_question,
        "node_by_question": node_by_question,
        "fields_by_node": fields_by_node,
        "critical_questions": set(),
        "critical_nodes": set(critical),
    })


def current(target="解剖学", phase="foundation"):
    return {"phase": phase, "recommended_study": [(target, 10)] if target else []}


def test_sparse_new_learner_reuses_current_foundation_target(monkeypatch):
    catalog(monkeypatch, {})
    result = build_shadow_judgment([], evidence(), current("生理学"), as_of=NOW)
    assert result["reason_code"] == "insufficient_coverage"
    assert result["target_field_id"] == 2
    assert result["question_count"] == 10
    assert result["shadow_only"] is True


def test_one_ordinary_wrong_does_not_commandeer_field(monkeypatch):
    catalog(monkeypatch, {"Q1": ("KN0001", 10)})
    attempts = [attempt("Q1", "KN0001", correct=False, confidence=2)]
    result = build_shadow_judgment(attempts, evidence(states={"KN0001": "repairing"}), current("解剖学"), as_of=NOW)
    assert result["reason_code"] == "insufficient_coverage"
    assert result["target_field_id"] == 1


def test_critical_safety_wrong_wins_first(monkeypatch):
    catalog(monkeypatch, {"Q1": ("KN0001", 8)}, critical={"KN0001"})
    attempts = [attempt("Q1", "KN0001", correct=False, confidence=2)]
    result = build_shadow_judgment(attempts, evidence(states={"KN0001": "repairing"}), current(), as_of=NOW)
    assert result["reason_code"] == "safety_repair"
    assert result["target_field_id"] == 8
    assert result["confidence"] == "high"


def test_cross_question_confident_wrong_triggers_j2(monkeypatch):
    catalog(monkeypatch, {"Q1": ("KN0001", 10), "Q2": ("KN0001", 10)})
    attempts = [
        attempt("Q1", "KN0001", correct=False, confidence=1, days=1),
        attempt("Q2", "KN0001", correct=False, confidence=2),
    ]
    result = build_shadow_judgment(
        attempts,
        evidence(states={"KN0001": "repairing"}, overrides={10: {"repairing_node_count": 1}}),
        current(), as_of=NOW,
    )
    assert result["reason_code"] == "confident_wrong_cluster"
    assert result["target_field_id"] == 10


def test_cross_question_wrong_without_confidence_triggers_j3(monkeypatch):
    catalog(monkeypatch, {"Q1": ("KN0001", 9), "Q2": ("KN0001", 9)})
    attempts = [
        attempt("Q1", "KN0001", correct=False, confidence=2, days=1),
        attempt("Q2", "KN0001", correct=False, confidence=3),
    ]
    result = build_shadow_judgment(
        attempts,
        evidence(states={"KN0001": "repairing"}, overrides={9: {"repairing_node_count": 1}}),
        current(), as_of=NOW,
    )
    assert result["reason_code"] == "repeated_wrong_cluster"
    assert result["target_field_id"] == 9


def test_lone_repeated_same_q_wrong_does_not_trigger_j3(monkeypatch):
    catalog(monkeypatch, {"Q1": ("KN0001", 9)})
    attempts = [
        attempt("Q1", "KN0001", correct=False, confidence=2, days=1),
        attempt("Q1", "KN0001", correct=False, confidence=2),
    ]
    result = build_shadow_judgment(
        attempts,
        evidence(states={"KN0001": "repairing"}, overrides={9: {"repairing_node_count": 1}}),
        current(), as_of=NOW,
    )
    assert result["reason_code"] == "insufficient_coverage"


def test_recheck_due_wins_when_no_urgent_repair(monkeypatch):
    catalog(monkeypatch, {})
    ev = evidence(overrides={7: {
        "recheck_due_node_count": 2,
        "retention_nodes": [
            {"canonical_node_id": "KN0007", "state": "recheck_due", "due_overdue_days": 5},
            {"canonical_node_id": "KN0008", "state": "recheck_due", "due_overdue_days": 2},
        ],
    }})
    result = build_shadow_judgment([], ev, current(), as_of=NOW)
    assert result["reason_code"] == "recheck_due"
    assert result["target_field_id"] == 7


def test_after_100_answers_sparse_field_uses_conservative_coverage(monkeypatch):
    catalog(monkeypatch, {})
    attempts = [attempt("X", "KN9999", correct=True, confidence=1) for _ in range(100)]
    ev = evidence(overrides={5: {"question_answer_count": 4, "node_coverage": {"percent": 3.0}}})
    result = build_shadow_judgment(attempts, ev, current(None, "analysis"), as_of=NOW)
    assert result["reason_code"] == "insufficient_coverage"
    assert result["target_field_id"] == 5


def test_uncertain_correct_cluster_triggers_stabilization(monkeypatch):
    catalog(monkeypatch, {
        "Q1": ("KN0001", 6), "Q2": ("KN0002", 6), "Q3": ("KN0003", 6),
    })
    filler = [attempt("X", "KN9999", correct=True, confidence=1) for _ in range(100)]
    attempts = filler + [
        attempt("Q1", "KN0001", correct=True, confidence=2),
        attempt("Q2", "KN0002", correct=True, confidence=3),
        attempt("Q3", "KN0003", correct=True, confidence=2),
    ]
    ev = evidence(overrides={6: {"question_answer_count": 10, "checking_node_count": 2}})
    result = build_shadow_judgment(attempts, ev, current(None, "analysis"), as_of=NOW)
    assert result["reason_code"] == "uncertain_correct_cluster"
    assert result["target_field_id"] == 6


def test_maintenance_has_no_target_and_uses_adaptive_daily(monkeypatch):
    catalog(monkeypatch, {})
    attempts = [attempt("X", "KN9999", correct=True, confidence=1, days=1) for _ in range(100)]
    result = build_shadow_judgment(attempts, evidence(), current(None, "analysis"), as_of=NOW)
    assert result["reason_code"] == "maintenance_only"
    assert result["target_field_id"] is None
    assert result["question_count"] == 30
    assert result["recommended_route"] == "adaptive_daily"


def test_unknown_answers_do_not_create_confirmed_weakness(monkeypatch):
    catalog(monkeypatch, {"Q1": ("KN0001", 9), "Q2": ("KN0001", 9)})
    attempts = [
        attempt("Q1", "KN0001", correct=False, unknown=True, days=1),
        attempt("Q2", "KN0001", correct=False, unknown=True),
    ]
    result = build_shadow_judgment(
        attempts,
        evidence(states={"KN0001": "repairing"}, overrides={9: {"repairing_node_count": 1}}),
        current(), as_of=NOW,
    )
    assert result["reason_code"] == "insufficient_coverage"


def test_high_same_day_volume_is_observation_not_block(monkeypatch):
    catalog(monkeypatch, {})
    attempts = [attempt("X", "KN9999", correct=True, confidence=1) for _ in range(60)]
    result = build_shadow_judgment(attempts, evidence(), current(), as_of=NOW)
    assert "high_same_day_volume" in result["observations"]
    assert result["question_count"] == 10


def test_comparison_labels_same_foundation_target_without_auto_scoring():
    shadow = {
        "target_field": "解剖学",
        "reason_code": "insufficient_coverage",
    }
    comparison = build_shadow_comparison(current("解剖学", "foundation"), shadow)
    assert comparison["label"] == "same_target_same_reason"


def test_symmetric_comparison_can_find_current_target_stronger():
    profiles = {
        "内科学": {"reason_rank": 1, "strongest_reason_code": "safety_repair"},
        "神経学": {"reason_rank": 3, "strongest_reason_code": "repeated_wrong_cluster"},
    }
    comparison = build_shadow_comparison(
        current("内科学", "analysis"),
        {"target_field": "神経学", "reason_code": "repeated_wrong_cluster"},
        profiles,
    )
    assert comparison["label"] == "different_target_current_has_stronger_evidence"
    assert comparison["shadow_reason_profile_consistent"] is True


def test_symmetric_comparison_can_find_shadow_target_stronger():
    profiles = {
        "内科学": {"reason_rank": 5, "strongest_reason_code": "insufficient_coverage"},
        "神経学": {"reason_rank": 2, "strongest_reason_code": "confident_wrong_cluster"},
    }
    comparison = build_shadow_comparison(
        current("内科学", "analysis"),
        {"target_field": "神経学", "reason_code": "confident_wrong_cluster"},
        profiles,
    )
    assert comparison["label"] == "different_target_shadow_has_stronger_evidence"


def test_equal_rank_different_targets_stays_insufficient():
    profiles = {
        "内科学": {"reason_rank": 5, "strongest_reason_code": "insufficient_coverage"},
        "神経学": {"reason_rank": 5, "strongest_reason_code": "insufficient_coverage"},
    }
    comparison = build_shadow_comparison(
        current("内科学", "analysis"),
        {"target_field": "神経学", "reason_code": "insufficient_coverage"},
        profiles,
    )
    assert comparison["label"] == "insufficient_evidence_to_judge"


def test_profiles_use_formal_safety_and_exclude_unknown(monkeypatch):
    catalog(monkeypatch, {"Q1": ("KN0001", 8)}, critical={"KN0001"})
    ev = evidence(states={"KN0001": "repairing"})
    unknown_profiles = build_field_judgment_evidence_profiles(
        [attempt("Q1", "KN0001", correct=False, confidence=None, unknown=True)], ev
    )
    assert unknown_profiles["F8"]["critical_safety_unresolved_count"] == 0
    profiles = build_field_judgment_evidence_profiles(
        [attempt("Q1", "KN0001", correct=False, confidence=1)], ev
    )
    assert profiles["F8"]["strongest_reason_code"] == "safety_repair"
    assert profiles["F8"]["reason_rank"] == 1


def test_profile_confident_wrong_requires_same_formal_threshold(monkeypatch):
    catalog(monkeypatch, {"Q1": ("KN0001", 10), "Q2": ("KN0002", 10)})
    attempts = [
        attempt("Q1", "KN0001", correct=False, confidence=1),
        attempt("Q2", "KN0002", correct=False, confidence=1),
    ]
    profiles = build_field_judgment_evidence_profiles(
        attempts,
        evidence(
            states={"KN0001": "repairing", "KN0002": "repairing"},
            overrides={10: {"repairing_node_count": 2}},
        ),
    )
    assert profiles["F10"]["distinct_confident_wrong_repairing_node_count"] == 2
    assert profiles["F10"]["strongest_reason_code"] == "confident_wrong_cluster"
