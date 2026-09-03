from copy import deepcopy
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pass_readiness as readiness
import phase11_formal_judgment as formal


BASE = datetime(2026, 9, 1, tzinfo=timezone.utc)


def _fixture(*, touched=25, repaired=0, recheck_due=0, stable=0, evaluable=120):
    total = 100
    repairing = 0
    checking = max(0, touched - repaired - recheck_due - stable - repairing)
    unseen = total - touched
    states = (
        ["stable"] * stable
        + ["repaired"] * repaired
        + ["recheck_due"] * recheck_due
        + ["repairing"] * repairing
        + ["checking"] * checking
        + ["unseen"] * unseen
    )
    canonical = [
        {"canonical_node_id": f"N{i+1}", "state": state}
        for i, state in enumerate(states)
    ]
    evidence = {
        "canonical_node_evidence": canonical,
        "fields": [{
            "field_id": 1,
            "field_name": "F1",
            "evaluable_answer_count": evaluable,
            "repairing_node_count": repairing,
        }],
    }
    counts = {state: states.count(state) for state in readiness.Counter(states)}
    progress = {
        "overall": {
            "total_unique_canonical_nodes": total,
            "touched_unique_canonical_nodes": touched,
            "state_counts": counts,
            "overall_progress_score": 0.0,
        },
    }
    ability = {}
    for idx, name in enumerate(readiness.ABILITIES):
        start = idx * 10 + 1
        ability[name] = {f"N{i}" for i in range(start, start + 10)}
    return evidence, progress, ability


def _active_record(*, confident=False, repeated=False):
    return {
        "active_evaluable_wrong_attempt_count": 1,
        "active_has_confident_wrong": confident,
        "active_weakness_evidence_level": (
            readiness.CROSS_QUESTION_WRONG if repeated else "SINGLE_WRONG"
        ),
    }


def _run(monkeypatch, *, evidence, progress, ability, active=None, attempts=None, trial=None, critical=None):
    active = active or {}
    monkeypatch.setattr(readiness, "_ABILITY_OPPORTUNITIES", ability)
    monkeypatch.setattr(
        readiness,
        "build_formal_context",
        lambda attempts, field_evidence, as_of=None: {
            "active_by_node": active,
            "active_field_facts": {},
        },
    )
    old_catalog = formal._CATALOG
    monkeypatch.setattr(
        formal,
        "_CATALOG",
        {**old_catalog, "critical_nodes": set(critical or [])},
    )
    return readiness.build_pass_readiness(
        attempts or [],
        field_evidence=evidence,
        progress=progress,
        trial100_records=trial,
    )


def test_empty_history_is_insufficient_evidence(monkeypatch):
    evidence, progress, ability = _fixture(touched=0, evaluable=0)
    result = _run(monkeypatch, evidence=evidence, progress=progress, ability=ability)
    assert result["status"] == "insufficient_evidence"
    assert result["pass_probability"] is None
    assert result["pass_guarantee"] is False
    assert result["missing_evidence"][0]["code"] == "trial100_not_recorded"


def test_high_accuracy_on_tiny_slice_cannot_create_readiness(monkeypatch):
    evidence, progress, ability = _fixture(touched=5, evaluable=20)
    evidence["fields"][0]["evaluable_accuracy"] = 1.0
    result = _run(monkeypatch, evidence=evidence, progress=progress, ability=ability)
    assert result["status"] == "insufficient_evidence"


def test_one_ordinary_wrong_does_not_flip_whole_learner_to_repair(monkeypatch):
    evidence, progress, ability = _fixture(touched=25, evaluable=120)
    result = _run(
        monkeypatch,
        evidence=evidence,
        progress=progress,
        ability=ability,
        active={"N1": _active_record()},
    )
    assert result["status"] == "building_coverage"
    assert result["components"]["repair_burden"]["material_active_repair"] is False


def test_material_active_repair_has_precedence_over_coverage(monkeypatch):
    evidence, progress, ability = _fixture(touched=25, evaluable=120)
    active = {f"N{i}": _active_record() for i in range(1, 4)}
    result = _run(monkeypatch, evidence=evidence, progress=progress, ability=ability, active=active)
    assert result["status"] == "repair_required"
    assert result["blocking_reasons"][0]["code"] == "material_active_repair_burden"


def test_confident_wrong_cluster_is_material_repair(monkeypatch):
    evidence, progress, ability = _fixture(touched=25, evaluable=120)
    active = {"N1": _active_record(confident=True), "N2": _active_record(confident=True)}
    result = _run(monkeypatch, evidence=evidence, progress=progress, ability=ability, active=active)
    assert result["status"] == "repair_required"


def test_repeated_wrong_cluster_is_material_repair(monkeypatch):
    evidence, progress, ability = _fixture(touched=25, evaluable=120)
    active = {"N1": _active_record(repeated=True), "N2": _active_record(repeated=True)}
    result = _run(monkeypatch, evidence=evidence, progress=progress, ability=ability, active=active)
    assert result["status"] == "repair_required"


def test_active_critical_safety_wrong_blocks_otherwise_strong_profile(monkeypatch):
    evidence, progress, ability = _fixture(touched=85, stable=60, evaluable=600)
    active = {"N1": _active_record()}
    result = _run(
        monkeypatch,
        evidence=evidence,
        progress=progress,
        ability=ability,
        active=active,
        critical={"N1"},
        trial=[{"timed_full_format": True, "supportive": True}],
    )
    assert result["status"] == "safety_attention_required"
    assert result["components"]["safety"]["ready"] is False


def test_repaired_is_not_stable_and_requires_retention_confirmation(monkeypatch):
    evidence, progress, ability = _fixture(touched=65, repaired=20, stable=10, evaluable=400)
    result = _run(monkeypatch, evidence=evidence, progress=progress, ability=ability)
    assert result["status"] == "retention_confirmation_needed"
    retention = result["components"]["retention"]
    assert retention["repaired_nodes"] == 20
    assert retention["stable_nodes"] == 10


def test_recheck_due_requires_retention_confirmation(monkeypatch):
    evidence, progress, ability = _fixture(touched=65, recheck_due=1, stable=30, evaluable=400)
    result = _run(monkeypatch, evidence=evidence, progress=progress, ability=ability)
    assert result["status"] == "retention_confirmation_needed"


def test_mixed_ability_blind_spot_keeps_building_coverage(monkeypatch):
    evidence, progress, ability = _fixture(touched=65, stable=30, evaluable=400)
    # Make PREDICT opportunity Nodes live almost entirely outside the touched set.
    ability = deepcopy(ability)
    ability["PREDICT"] = {f"N{i}" for i in range(91, 101)}
    result = _run(monkeypatch, evidence=evidence, progress=progress, ability=ability)
    assert result["status"] == "building_coverage"
    assert "PREDICT" in result["caution_reasons"][0]["facts"]["under_broad_abilities"]


def test_broad_profile_without_full_format_support_is_approaching(monkeypatch):
    evidence, progress, ability = _fixture(touched=65, stable=30, evaluable=400)
    result = _run(monkeypatch, evidence=evidence, progress=progress, ability=ability)
    assert result["status"] == "approaching_readiness"
    assert any(item["code"] == "trial100_not_recorded" for item in result["missing_evidence"])


def test_strong_consistent_profile_with_supportive_trial100_is_readiness_supported(monkeypatch):
    evidence, progress, ability = _fixture(touched=85, stable=60, evaluable=700)
    result = _run(
        monkeypatch,
        evidence=evidence,
        progress=progress,
        ability=ability,
        trial=[{"timed_full_format": True, "supportive": True}],
    )
    assert result["status"] == "readiness_supported"
    assert result["components"]["trial100"]["has_supportive_full_format_evidence"] is True


def test_activity_volume_without_new_mastery_does_not_improve_status(monkeypatch):
    evidence, progress, ability = _fixture(touched=25, evaluable=120)
    few = [{"answered_at": BASE}]
    many = [{"answered_at": BASE + timedelta(minutes=i)} for i in range(500)]
    a = _run(monkeypatch, evidence=evidence, progress=progress, ability=ability, attempts=few)
    b = _run(monkeypatch, evidence=evidence, progress=progress, ability=ability, attempts=many)
    assert a["status"] == b["status"] == "building_coverage"
    assert b["components"]["activity_context"]["mastery_credit_applied"] is False


def test_shuffled_attempt_order_is_deterministic_for_status(monkeypatch):
    evidence, progress, ability = _fixture(touched=25, evaluable=120)
    attempts = [
        {"question_id": "Q1", "answered_at": BASE},
        {"question_id": "Q2", "answered_at": BASE + timedelta(days=1)},
    ]
    first = _run(monkeypatch, evidence=evidence, progress=progress, ability=ability, attempts=attempts)
    second = _run(monkeypatch, evidence=evidence, progress=progress, ability=ability, attempts=list(reversed(attempts)))
    assert first["status"] == second["status"]
    assert first["components"]["activity_context"] == second["components"]["activity_context"]


def test_evaluator_does_not_import_persisted_user_node_state_as_authority():
    source = (Path(__file__).resolve().parents[1] / "pass_readiness.py").read_text(encoding="utf-8")
    assert "get_user_node_states" not in source
    assert "user_node_state" not in source
