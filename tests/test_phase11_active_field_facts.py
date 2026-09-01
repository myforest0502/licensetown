from knowledge_node_weakness_evidence import (
    CROSS_QUESTION_CONFIDENT_WRONG,
    CROSS_QUESTION_WRONG,
    NO_WRONG_EVIDENCE,
    REPEATED_SAME_QUESTION_WRONG,
    SINGLE_WRONG,
)
from phase11_active_field_facts import build_active_field_facts


def node(
    *,
    wrong_qs,
    confident_qs=(),
    level=SINGLE_WRONG,
):
    return {
        "active_evaluable_wrong_question_ids": list(wrong_qs),
        "active_confident_wrong_question_ids": list(confident_qs),
        "active_weakness_evidence_level": level,
    }


def test_single_field_active_wrong_stays_in_observed_source_field():
    facts = build_active_field_facts(
        {"KN1": node(wrong_qs=["Q1"])},
        field_by_question={"Q1": 3},
    )
    assert set(facts) == {3}
    assert facts[3]["active_evaluable_wrong_repairing_node_count"] == 1
    assert facts[3]["active_wrong_question_ids"] == ["Q1"]


def test_static_unobserved_member_field_is_not_invented():
    facts = build_active_field_facts(
        {"KN1": node(wrong_qs=["Q1"])},
        field_by_question={"Q1": 3, "QOTHER": 9},
    )
    assert 9 not in facts


def test_cross_question_wrong_spanning_two_observed_fields_contributes_to_both():
    facts = build_active_field_facts(
        {"KN1": node(
            wrong_qs=["Q1", "Q2"],
            level=CROSS_QUESTION_WRONG,
        )},
        field_by_question={"Q1": 3, "Q2": 9},
    )
    assert facts[3]["active_cross_question_wrong_node_count"] == 1
    assert facts[9]["active_cross_question_wrong_node_count"] == 1
    assert facts[3]["active_repeated_weakness_node_count"] == 1
    assert facts[9]["active_repeated_weakness_node_count"] == 1


def test_cross_confident_node_is_node_level_in_each_observed_source_field():
    facts = build_active_field_facts(
        {"KN1": node(
            wrong_qs=["Q1", "Q2"],
            confident_qs=["Q1"],
            level=CROSS_QUESTION_CONFIDENT_WRONG,
        )},
        field_by_question={"Q1": 3, "Q2": 9},
    )
    assert facts[3]["active_cross_question_confident_wrong_node_count"] == 1
    assert facts[9]["active_cross_question_confident_wrong_node_count"] == 1
    assert facts[3]["active_confident_wrong_repairing_node_count"] == 1
    assert facts[9]["active_confident_wrong_repairing_node_count"] == 0


def test_critical_safety_is_attributed_only_where_active_wrong_was_observed():
    facts = build_active_field_facts(
        {"KN1": node(wrong_qs=["Q1"])},
        field_by_question={"Q1": 8},
        critical_nodes={"KN1"},
    )
    assert facts[8]["critical_safety_unresolved_count"] == 1


def test_unknown_only_or_no_wrong_fact_creates_no_field_weakness():
    facts = build_active_field_facts(
        {"KN1": node(wrong_qs=[], level=NO_WRONG_EVIDENCE)},
        field_by_question={"Q1": 8},
        critical_nodes={"KN1"},
    )
    assert facts == {}


def test_repeated_same_question_counts_as_repeated_in_its_observed_field():
    facts = build_active_field_facts(
        {"KN1": node(
            wrong_qs=["Q1"],
            level=REPEATED_SAME_QUESTION_WRONG,
        )},
        field_by_question={"Q1": 4},
    )
    assert facts[4]["active_repeated_weakness_node_count"] == 1
    assert facts[4]["active_cross_question_wrong_node_count"] == 0


def test_multiple_nodes_accumulate_without_double_counting_one_node_per_field():
    facts = build_active_field_facts(
        {
            "KN1": node(wrong_qs=["Q1", "Q2"], level=CROSS_QUESTION_WRONG),
            "KN2": node(wrong_qs=["Q3"], confident_qs=["Q3"]),
        },
        field_by_question={"Q1": 5, "Q2": 5, "Q3": 5},
    )
    assert facts[5]["active_evaluable_wrong_repairing_node_count"] == 2
    assert facts[5]["active_cross_question_wrong_node_count"] == 1
    assert facts[5]["active_confident_wrong_repairing_node_count"] == 1
    assert facts[5]["active_node_ids"] == ["KN1", "KN2"]
