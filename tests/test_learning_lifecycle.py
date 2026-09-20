from copy import deepcopy

import pytest

from licensetown.pt.field_learning_target_shadow import build_field_targets
from licensetown.pt.field_progress import build_field_progress
from licensetown.pt.learning_lifecycle import build_learning_lifecycle


def snapshots(*, covered=False, supply=60, state="checking", stage=None, checkpoint=None):
    fields, catalog, states = [], [], []
    for field_id in range(1, 19):
        node_id = f"N{field_id}"
        actual = state if covered else "unseen"
        fields.append({
            "field_id": field_id, "field_name": str(field_id),
            "total_question_count": supply, "total_canonical_node_count": 1,
            "attempted_canonical_node_count": int(covered),
            "answered_unique_question_count": min(60, supply) if covered else 0,
            "evaluable_answer_count": min(60, supply) if covered else 0,
            "evaluable_accuracy": 0.8 if covered else None,
            "state_counts": {actual: 1}, "question_coverage": {},
        })
        catalog.append({"canonical_node_id": node_id, "field_ids": [field_id], "state": actual})
        if covered:
            states.append({"canonical_node_id": node_id, "state": actual,
                           "retention_stage": stage, "retention_checkpoint": checkpoint})
    evidence = {"status": "evidence_only", "fields": fields,
                "canonical_node_evidence": catalog, "multi_field_node_count": 0,
                "canonical_node_membership_total": 18}
    return evidence, build_field_targets(evidence, build_field_progress(evidence)), states


def test_new_user_remains_coverage():
    result = build_learning_lifecycle(*snapshots(), critical_safety_unresolved_count=0)
    assert result["phase"] == "coverage"
    assert not result["coverage_checkpoint_reached"]
    assert not result["repair_priority"] and not result["retention_priority"]


def test_partial_fields_and_each_checkpoint_boundary():
    for key, value in (("evaluable_answer_count", 59),
                       ("answered_unique_question_count", 59),
                       ("attempted_canonical_node_count", 0)):
        evidence, targets, states = snapshots(covered=True)
        evidence["fields"][-1][key] = value
        result = build_learning_lifecycle(evidence, targets, states)
        assert not result["coverage_checkpoint_reached"]
        assert result["phase"] == "coverage"
    evidence, targets, states = snapshots(covered=True)
    with pytest.raises(ValueError, match="one row"):
        build_learning_lifecycle({**evidence, "fields": evidence["fields"][:-1]}, targets, states)


def test_all_fields_checkpoint_without_mastery_claim():
    result = build_learning_lifecycle(*snapshots(covered=True), critical_safety_unresolved_count=0)
    assert result["coverage_checkpoint_reached"]
    assert result["phase"] == "depth_repair"
    assert not result["repair_priority"]
    assert result["provisional"] and not result["selection_authority"]


def test_small_supply_assessing_does_not_block_first_pass():
    inputs = snapshots(covered=True, supply=15)
    assert all(row["field_state"] == "assessing" for row in inputs[1]["fields"])
    assert all(not row["evaluation"]["evidence_sufficient"] for row in inputs[1]["fields"])
    assert build_learning_lifecycle(*inputs)["coverage_checkpoint_reached"]


def test_current_repair_overrides_coverage_and_retention():
    evidence, targets, states = snapshots(covered=True, state="recheck_due", checkpoint="day3")
    states[0]["state"] = evidence["canonical_node_evidence"][0]["state"] = "repairing"
    result = build_learning_lifecycle(evidence, targets, states, critical_safety_unresolved_count=0)
    assert result["phase"] == "depth_repair" and result["repair_priority"]
    assert not result["retention_priority"]
    assert result["evidence"]["current_repairing_nodes"] == 1


def test_critical_safety_does_not_fabricate_coverage():
    result = build_learning_lifecycle(*snapshots(), critical_safety_unresolved_count=1)
    assert result["phase"] == "depth_repair" and result["repair_priority"]
    assert not result["coverage_checkpoint_reached"]
    assert "critical_safety_unresolved" in result["reason_codes"]


def test_missing_safety_is_not_zero_or_safe():
    result = build_learning_lifecycle(*snapshots())
    assert result["evidence"]["critical_safety_unresolved_count"] is None
    assert result["missing_evidence"] == ["critical_safety_unresolved_count"]
    assert "safety_evidence_unavailable" in result["reason_codes"]
    with pytest.raises(ValueError):
        build_learning_lifecycle(*snapshots(), critical_safety_unresolved_count=-1)


def test_old_wrong_does_not_reactivate_repaired_or_stable_nodes():
    for state, stage, checkpoint in (("repaired", "repair_confirmed", "day3"),
                                     ("stable", "day7_passed", "day30"),
                                     ("stable", "durable", None)):
        inputs = snapshots(covered=True, state=state, stage=stage, checkpoint=checkpoint)
        for node in inputs[2]:
            node.update(wrong_question_count=7, evidence_level="CROSS_QUESTION_CONFIDENT_WRONG")
        result = build_learning_lifecycle(*inputs, critical_safety_unresolved_count=0)
        assert not result["repair_priority"]
        assert result["phase"] == "retention_readiness"


def test_formal_retention_due_and_future_checkpoint_have_different_priority():
    for checkpoint in ("day3", "day7", "day30"):
        evidence, targets, states = snapshots(covered=True, state="recheck_due", checkpoint=checkpoint)
        evidence["fields"][-1]["evaluable_answer_count"] = 0
        result = build_learning_lifecycle(evidence, targets, states, critical_safety_unresolved_count=0)
        assert result["retention_priority"] and not result["coverage_checkpoint_reached"]
        assert result["phase"] == "retention_readiness"
    evidence, targets, states = snapshots(covered=True, state="repaired", checkpoint="day3")
    evidence["fields"][-1]["evaluable_answer_count"] = 0
    assert build_learning_lifecycle(evidence, targets, states)["phase"] == "coverage"
    with pytest.raises(ValueError, match="must match"):
        build_learning_lifecycle(evidence, targets, [])


def test_pure_deterministic_shortage_ignored_and_unique_node_counts():
    inputs = snapshots()
    inputs[0]["strategy_fallback_reason"] = "eligible_supply_insufficient"
    before = deepcopy(inputs)
    first = build_learning_lifecycle(*inputs)
    assert first == build_learning_lifecycle(*inputs)
    assert inputs == before
    assert first["phase"] == "coverage" and not first["coverage_checkpoint_reached"]
    evidence, targets, states = snapshots(covered=True, state="repairing")
    # Multiple field memberships must not multiply the single formal Node count.
    evidence["canonical_node_evidence"] = [{"canonical_node_id": "N1",
        "field_ids": list(range(1, 19)), "state": "repairing"}]
    result = build_learning_lifecycle(evidence, targets, states[:1])
    assert result["evidence"]["current_repairing_nodes"] == 1
    with pytest.raises(ValueError, match="unique"):
        build_learning_lifecycle(evidence, targets, states[:1] * 2)
