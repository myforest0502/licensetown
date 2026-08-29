from knowledge_node_repair_evidence import (
    DIFFERENT_QUESTION_STRONG,
    DIFFERENT_QUESTION_WEAK,
    SAME_QUESTION,
    classify_repair_confirmation,
)


def test_same_question_is_never_cross_question_confirmation():
    assert classify_repair_confirmation("Q269", "Q269") == SAME_QUESTION


def test_different_existing_demand_is_strong_confirmation():
    assert classify_repair_confirmation("Q269", "Q361") == DIFFERENT_QUESTION_STRONG


def test_reword_like_same_demand_fails_closed_as_weak():
    assert classify_repair_confirmation("Q1091", "Q1544") == DIFFERENT_QUESTION_WEAK


def test_unknown_metadata_fails_closed_as_weak():
    assert classify_repair_confirmation("Q99999", "Q88888") == DIFFERENT_QUESTION_WEAK
