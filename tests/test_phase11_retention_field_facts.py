from phase11_retention_field_facts import (
    build_j4_candidates,
    build_retention_field_facts,
)


def state(
    node,
    *,
    status="recheck_due",
    ref=None,
    overdue=0,
):
    return {
        "canonical_node_id": node,
        "state": status,
        "retention_reference_question_id": ref,
        "due_overdue_days": overdue,
    }


def test_recheck_due_is_attributed_to_reference_question_field_only():
    facts = build_retention_field_facts(
        [state("KN1", ref="Q1", overdue=3)],
        field_by_question={"Q1": 7, "QSTATIC": 9},
    )
    assert set(facts["by_field"]) == {7}
    assert facts["by_field"][7]["canonical_node_ids"] == ["KN1"]
    assert facts["unattributed"] == []


def test_non_due_states_do_not_create_j4_evidence():
    facts = build_retention_field_facts(
        [state("KN1", status="repaired", ref="Q1", overdue=0)],
        field_by_question={"Q1": 7},
    )
    assert facts["by_field"] == {}
    assert facts["unattributed"] == []


def test_missing_reference_is_unattributed_not_duplicated():
    facts = build_retention_field_facts(
        [state("KN1", ref=None, overdue=4)],
        field_by_question={"Q1": 7},
    )
    assert facts["by_field"] == {}
    assert facts["unattributed"][0]["canonical_node_id"] == "KN1"
    assert facts["unattributed"][0]["retention_reference_question_id"] is None


def test_unmapped_reference_is_unattributed():
    facts = build_retention_field_facts(
        [state("KN1", ref="QUNKNOWN", overdue=2)],
        field_by_question={"Q1": 7},
    )
    assert facts["by_field"] == {}
    assert facts["unattributed"][0]["reason"] == "missing_or_unmapped_retention_reference_question"


def test_field_aggregates_count_max_and_total_overdue():
    facts = build_retention_field_facts(
        [
            state("KN1", ref="Q1", overdue=2),
            state("KN2", ref="Q2", overdue=5),
        ],
        field_by_question={"Q1": 7, "Q2": 7},
    )
    field = facts["by_field"][7]
    assert field["recheck_due_node_count"] == 2
    assert field["max_overdue_days"] == 5
    assert field["total_overdue_days"] == 7


def test_j4_candidate_order_matches_existing_policy():
    facts = {
        "by_field": {
            1: {"recheck_due_node_count": 2, "max_overdue_days": 3, "total_overdue_days": 5},
            2: {"recheck_due_node_count": 2, "max_overdue_days": 5, "total_overdue_days": 5},
            3: {"recheck_due_node_count": 2, "max_overdue_days": 5, "total_overdue_days": 8},
            4: {"recheck_due_node_count": 1, "max_overdue_days": 20, "total_overdue_days": 20},
        },
        "unattributed": [],
    }
    candidates = build_j4_candidates(facts)
    assert [item["field_id"] for item in candidates] == [3, 2, 1, 4]


def test_j4_field_id_is_final_tie_break():
    facts = {
        "by_field": {
            2: {"recheck_due_node_count": 1, "max_overdue_days": 2, "total_overdue_days": 2},
            1: {"recheck_due_node_count": 1, "max_overdue_days": 2, "total_overdue_days": 2},
        },
        "unattributed": [],
    }
    assert [item["field_id"] for item in build_j4_candidates(facts)] == [1, 2]
