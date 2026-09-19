from learning_strategy_context_shadow import derive_recommendation_plan_context


def test_observed_recommendation_plan_history_does_not_show_three_completed_blocks_before_any_plan():
    # Anonymous aggregate from Production SELECT-only audit. These are the 14
    # observed recommendation-plan fields and the number of dashboard
    # recommendation questions actually completed after each plan and before the
    # next one. Plan goals are deliberately not treated as completion.
    observations = [
        {"field_id": 4, "goal": 10, "completed_recommendation_questions": 10},
        {"field_id": 11, "goal": 10, "completed_recommendation_questions": 10},
        {"field_id": 9, "goal": 10, "completed_recommendation_questions": 30},
        {"field_id": 13, "goal": 10, "completed_recommendation_questions": 20},
        {"field_id": 2, "goal": 10, "completed_recommendation_questions": 10},
        {"field_id": 2, "goal": 10, "completed_recommendation_questions": 10},
        {"field_id": 2, "goal": 10, "completed_recommendation_questions": 10},
        {"field_id": 2, "goal": 10, "completed_recommendation_questions": 20},
        {"field_id": 2, "goal": 10, "completed_recommendation_questions": 10},
        {"field_id": 9, "goal": 10, "completed_recommendation_questions": 40},
        {"field_id": 7, "goal": 10, "completed_recommendation_questions": 10},
        {"field_id": 7, "goal": 10, "completed_recommendation_questions": 10},
        {"field_id": 8, "goal": 10, "completed_recommendation_questions": 10},
        {"field_id": 8, "goal": 10, "completed_recommendation_questions": 10},
    ]

    result = derive_recommendation_plan_context(observations)
    rows = result["rows"]

    assert result["plan_count"] == 14
    assert max(row["consecutive_field_blocks"] for row in rows) == 1
    assert result["max_completed_30q_equivalent_after"] == 2

    physiology = [row for row in rows if row["field_id"] == 2]
    assert [row["consecutive_field_blocks"] for row in physiology] == [0, 0, 0, 1, 1]
    assert [row["observed_same_field_completed_questions_before"] for row in physiology] == [0, 10, 20, 30, 50]
    assert physiology[-1]["observed_same_field_completed_questions_after"] == 60

    # Historical recommendation plans cannot establish that post-weakness
    # additional training blocks were completed, so that context remains unknown.
    assert all(row["additional_blocks_completed"] is None for row in rows)
    assert all(not row["additional_blocks_completed_available"] for row in rows)
