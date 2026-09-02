from knowledge_node_repair_evidence import (
    DIFFERENT_QUESTION_STRONG,
    classify_repair_confirmation,
)
from question_bank import (
    get_answer,
    get_explanation,
    get_question,
    get_question_tag,
    question_count,
)


ITEMS = {
    "Q1606": ("KN0194", ("Q195", "Q1599"), "assessment_selection", "MEASURE", "B"),
    "Q1607": ("KN0676", ("Q684", "Q1602"), "assessment_selection", "MEASURE", "A"),
    "Q1608": ("KN0025", ("Q25", "Q1596"), "safety_priority", "DECIDE", "D"),
    "Q1609": ("KN0329", ("Q331", "Q1600"), "assessment_selection", "MEASURE", "A"),
    "Q1610": ("KN0697", ("Q705", "Q1603"), "safety_priority", "DECIDE", "C"),
}


def test_phase2_batch1_records_are_complete_and_mapped():
    assert question_count() == 1630
    for q_id, (node_id, _sources, task, ability, correct) in ITEMS.items():
        question = get_question(q_id)
        answer = get_answer(q_id)
        explanation = get_explanation(q_id)
        tag = get_question_tag(q_id)
        assert question["source"] == "O" and question["exam"] is None
        assert question["management_code"].endswith("-O")
        assert len(question["choices"]) == 5
        assert answer["display_answer"] == correct
        assert answer["accepted_answer_sets"] == [[correct]]
        assert answer["answer_basis"] == "LT_original"
        assert set(explanation["choice_explanations"]) == set(question["choices"])
        assert tag["knowledge_node_id"] == node_id
        assert tag["task"] == task
        assert tag["primary_ability"] == ability
        assert tag["safety"] == "moderate"
        assert tag["source"] == "original"


def test_each_new_item_is_formal_strong_against_both_active_wrong_questions():
    for q_id, (_node_id, sources, _task, _ability, _correct) in ITEMS.items():
        for source_q in sources:
            assert (
                classify_repair_confirmation(source_q, q_id)
                == DIFFERENT_QUESTION_STRONG
            )
            assert (
                classify_repair_confirmation(q_id, source_q)
                == DIFFERENT_QUESTION_STRONG
            )
