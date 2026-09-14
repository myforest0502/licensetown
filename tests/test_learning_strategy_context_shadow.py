import pytest

from learning_strategy_context_shadow import derive_recommendation_plan_context


def test_consecutive_blocks_use_completed_questions_not_plan_goal():
    result = derive_recommendation_plan_context([
        {"field_id": 2, "goal": 999, "completed_recommendation_questions": 10},
        {"field_id": 2, "goal": 999, "completed_recommendation_questions": 10},
        {"field_id": 2, "goal": 999, "completed_recommendation_questions": 10},
    ])

    rows = result["rows"]
    assert [row["consecutive_field_blocks"] for row in rows] == [0, 0, 0]
    assert rows[-1]["completed_30q_equivalent_after"] == 1
    assert result["max_observed_same_field_completed_questions"] == 30


def test_context_is_pre_plan_and_does_not_leak_future_completion():
    result = derive_recommendation_plan_context([
        {"field_id": 2, "goal": 10, "completed_recommendation_questions": 10},
        {"field_id": 2, "goal": 10, "completed_recommendation_questions": 10},
        {"field_id": 2, "goal": 10, "completed_recommendation_questions": 10},
        {"field_id": 2, "goal": 10, "completed_recommendation_questions": 20},
        {"field_id": 2, "goal": 10, "completed_recommendation_questions": 10},
    ])

    rows = result["rows"]
    assert [row["observed_same_field_completed_questions_before"] for row in rows] == [0, 10, 20, 30, 50]
    assert [row["consecutive_field_blocks"] for row in rows] == [0, 0, 0, 1, 1]
    assert rows[-1]["observed_same_field_completed_questions_after"] == 60
    assert rows[-1]["completed_30q_equivalent_after"] == 2
    assert result["max_completed_30q_equivalent_after"] == 2


def test_field_change_resets_concentration_streak():
    result = derive_recommendation_plan_context([
        {"field_id": 2, "completed_recommendation_questions": 40},
        {"field_id": 2, "completed_recommendation_questions": 20},
        {"field_id": 9, "completed_recommendation_questions": 30},
        {"field_id": 9, "completed_recommendation_questions": 10},
    ])

    rows = result["rows"]
    assert rows[1]["consecutive_field_blocks"] == 1
    assert rows[2]["consecutive_field_blocks"] == 0
    assert rows[3]["consecutive_field_blocks"] == 1


def test_additional_blocks_are_never_invented_from_generic_recommendations():
    result = derive_recommendation_plan_context([
        {"field_id": 8, "goal": 10, "completed_recommendation_questions": 120},
    ])
    row = result["rows"][0]
    assert row["additional_blocks_completed"] is None
    assert row["additional_blocks_completed_available"] is False


@pytest.mark.parametrize(
    "row",
    [
        {"field_id": 0, "completed_recommendation_questions": 10},
        {"field_id": 19, "completed_recommendation_questions": 10},
        {"field_id": 2, "completed_recommendation_questions": -1},
        {"field_id": "x", "completed_recommendation_questions": 10},
    ],
)
def test_invalid_context_input_is_rejected(row):
    with pytest.raises(ValueError):
        derive_recommendation_plan_context([row])
