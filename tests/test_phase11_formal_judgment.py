from datetime import datetime, timedelta, timezone

import knowledge_node_state_transition as transition
import phase11_formal_judgment as formal
from knowledge_node_repair_evidence import DIFFERENT_QUESTION_STRONG, DIFFERENT_QUESTION_WEAK


NOW = datetime(2026, 9, 1, 9, 0, tzinfo=timezone.utc)


def attempt(
    q,
    *,
    node="KN0268",
    correct,
    confidence=None,
    minute=0,
    days=0,
    unknown=False,
):
    return {
        "id": days * 10000 + minute + 1,
        "event_key": f"e-{q}-{days}-{minute}-{confidence}-{correct}",
        "user_id": "u",
        "question_id": q,
        "knowledge_node_id": node,
        "selected_answers": [] if unknown else ["A"],
        "answer_status": "unknown" if unknown else "answered",
        "is_correct": correct,
        "confidence": confidence,
        "answered_at": NOW + timedelta(days=days, minutes=minute),
        "attempt_position": 1,
    }


def classifier(strong_pairs):
    strong_pairs = set(strong_pairs)

    def classify(old, new):
        return DIFFERENT_QUESTION_STRONG if (old, new) in strong_pairs else DIFFERENT_QUESTION_WEAK

    return classify


def catalog(monkeypatch, mapping, *, critical=()):
    monkeypatch.setattr(formal, "_CATALOG", {
        "field_by_question": dict(mapping),
        "critical_nodes": set(critical),
    })


def field_evidence(overrides=None):
    overrides = overrides or {}
    fields = []
    for field_id, values in overrides.items():
        base = {
            "field_id": field_id,
            "field_name": formal.CATEGORY_NAMES[field_id],
            "question_answer_count": 10,
            "question_correct_count": 8,
            "question_accuracy": 0.8,
            "evaluable_answer_count": 10,
            "evaluable_correct_count": 8,
            "evaluable_accuracy": 0.8,
            "unknown_answer_count": 0,
            "node_coverage": {"percent": 20.0},
            "repairing_node_count": 0,
            "checking_node_count": 0,
        }
        base.update(values)
        fields.append(base)
    return {"fields": fields, "canonical_node_evidence": []}


def current(field_id=None, phase="analysis"):
    if field_id is None:
        return {"phase": phase, "recommended_study": []}
    return {
        "phase": phase,
        "recommended_study": [(formal.CATEGORY_NAMES[field_id], 10)],
    }


def test_foundation_under_100_preserves_current_target(monkeypatch):
    catalog(monkeypatch, {})
    result = formal.build_formal_shadow_judgment(
        [],
        field_evidence({2: {"question_answer_count": 0, "evaluable_answer_count": 0}}),
        current(2, "foundation"),
        as_of=NOW,
    )
    assert result["reason_code"] == "insufficient_coverage"
    assert result["target_field_id"] == 2
    assert result["question_count"] == 10


def test_current_cycle_cross_confident_wrong_triggers_j2(monkeypatch):
    catalog(monkeypatch, {"Q1": 10, "Q2": 10})
    attempts = [
        attempt("Q1", correct=False, confidence=1),
        attempt("Q2", correct=False, confidence=2, minute=1),
    ]
    result = formal.build_formal_shadow_judgment(
        attempts,
        field_evidence({10: {"repairing_node_count": 1}}),
        current(),
        as_of=NOW,
    )
    assert result["reason_code"] == "confident_wrong_cluster"
    assert result["target_field_id"] == 10


def test_old_cross_confident_does_not_revive_after_repair_and_new_unknown(monkeypatch):
    catalog(monkeypatch, {"Q1": 10, "Q2": 10, "Q3": 10, "Q4": 10})
    monkeypatch.setattr(
        transition,
        "classify_repair_confirmation",
        classifier({("Q1", "Q3"), ("Q2", "Q3")}),
    )
    attempts = [
        attempt("Q1", correct=False, confidence=1),
        attempt("Q2", correct=False, confidence=2, minute=1),
        attempt("Q3", correct=True, confidence=1, minute=2),
        attempt("Q4", correct=False, confidence=None, minute=3, unknown=True),
    ]
    result = formal.build_formal_shadow_judgment(
        attempts,
        field_evidence({10: {
            "question_answer_count": 4,
            "evaluable_answer_count": 3,
            "unknown_answer_count": 1,
            "repairing_node_count": 1,
        }}),
        current(10, "foundation"),
        as_of=NOW,
    )
    assert result["reason_code"] == "insufficient_coverage"
    assert result["reason_code"] != "confident_wrong_cluster"


def test_old_cross_wrong_plus_one_new_wrong_is_not_j3_cross_wrong(monkeypatch):
    catalog(monkeypatch, {"Q1": 9, "Q2": 9, "Q3": 9, "Q4": 9})
    monkeypatch.setattr(
        transition,
        "classify_repair_confirmation",
        classifier({("Q1", "Q3"), ("Q2", "Q3")}),
    )
    attempts = [
        attempt("Q1", correct=False, confidence=2),
        attempt("Q2", correct=False, confidence=3, minute=1),
        attempt("Q3", correct=True, confidence=1, minute=2),
        attempt("Q4", correct=False, confidence=2, minute=3),
    ]
    result = formal.build_formal_shadow_judgment(
        attempts,
        field_evidence({9: {"repairing_node_count": 1}}),
        current(9, "foundation"),
        as_of=NOW,
    )
    assert result["reason_code"] == "insufficient_coverage"


def test_critical_unknown_only_does_not_trigger_j1(monkeypatch):
    catalog(monkeypatch, {"Q1": 8}, critical={"KN0268"})
    result = formal.build_formal_shadow_judgment(
        [attempt("Q1", correct=False, unknown=True)],
        field_evidence({8: {
            "question_answer_count": 1,
            "evaluable_answer_count": 0,
            "unknown_answer_count": 1,
            "repairing_node_count": 1,
        }}),
        current(8, "foundation"),
        as_of=NOW,
    )
    assert result["reason_code"] == "insufficient_coverage"


def test_current_cycle_critical_real_wrong_still_triggers_j1(monkeypatch):
    catalog(monkeypatch, {"Q1": 8}, critical={"KN0268"})
    result = formal.build_formal_shadow_judgment(
        [attempt("Q1", correct=False, confidence=2)],
        field_evidence({8: {"repairing_node_count": 1}}),
        current(),
        as_of=NOW,
    )
    assert result["reason_code"] == "safety_repair"
    assert result["target_field_id"] == 8


def test_repaired_due_uses_reference_question_field_for_j4(monkeypatch):
    catalog(monkeypatch, {"Q1": 3, "Q2": 7})
    monkeypatch.setattr(
        transition,
        "classify_repair_confirmation",
        classifier({("Q1", "Q2")}),
    )
    attempts = [
        attempt("Q1", correct=False, confidence=2),
        attempt("Q2", correct=True, confidence=1, minute=1),
    ]
    result = formal.build_formal_shadow_judgment(
        attempts,
        field_evidence({3: {}, 7: {}}),
        current(),
        as_of=NOW + timedelta(days=8),
    )
    assert result["reason_code"] == "recheck_due"
    assert result["target_field_id"] == 7


def test_post_100_j5_uses_evaluable_count_not_unknown_exposure(monkeypatch):
    catalog(monkeypatch, {})
    filler = [
        attempt(f"X{i}", node=f"KN{i}", correct=True, confidence=1, minute=i)
        for i in range(100)
    ]
    result = formal.build_formal_shadow_judgment(
        filler,
        field_evidence({5: {
            "question_answer_count": 10,
            "evaluable_answer_count": 0,
            "unknown_answer_count": 10,
            "node_coverage": {"percent": 5.0},
        }}),
        current(),
        as_of=NOW,
    )
    assert result["reason_code"] == "insufficient_coverage"
    assert result["target_field_id"] == 5
    assert "field_evaluable_answer_count=0" in result["evidence"]


def test_j6_uses_evaluable_denominator(monkeypatch):
    catalog(monkeypatch, {"Q1": 6, "Q2": 6, "Q3": 6})
    filler = [
        attempt(f"X{i}", node=f"KN{i}", correct=True, confidence=1, minute=i)
        for i in range(100)
    ]
    attempts = filler + [
        attempt("Q1", node="KNA", correct=True, confidence=2, minute=101),
        attempt("Q2", node="KNB", correct=True, confidence=3, minute=102),
        attempt("Q3", node="KNC", correct=True, confidence=2, minute=103),
    ]
    result = formal.build_formal_shadow_judgment(
        attempts,
        field_evidence({6: {
            "question_answer_count": 5,
            "evaluable_answer_count": 3,
            "unknown_answer_count": 2,
            "checking_node_count": 3,
        }}),
        current(),
        as_of=NOW,
    )
    assert result["reason_code"] == "insufficient_coverage"


def test_multi_field_static_membership_is_not_invented_for_active_wrong(monkeypatch):
    catalog(monkeypatch, {"Q1": 3})
    result = formal.build_formal_shadow_judgment(
        [attempt("Q1", correct=False, confidence=1)],
        field_evidence({3: {}, 9: {}}),
        current(3, "foundation"),
        as_of=NOW,
    )
    assert result["target_field_id"] != 9


def test_profile_reason_matches_formal_shadow_target(monkeypatch):
    catalog(monkeypatch, {"Q1": 10, "Q2": 10})
    attempts = [
        attempt("Q1", correct=False, confidence=1),
        attempt("Q2", correct=False, confidence=2, minute=1),
    ]
    evidence = field_evidence({10: {"repairing_node_count": 1}})
    shadow = formal.build_formal_shadow_judgment(
        attempts, evidence, current(), as_of=NOW
    )
    profiles = formal.build_formal_field_profiles(
        attempts, evidence, as_of=NOW
    )
    assert profiles[shadow["target_field"]]["strongest_reason_code"] == shadow["reason_code"]
