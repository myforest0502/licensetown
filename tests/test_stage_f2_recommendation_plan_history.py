from learning_strategy_context_shadow import derive_recommendation_plan_context


# Anonymous aggregate observations from the Stage F Production READ-ONLY audit.
# No learner identifier, question ID, or attempt-level history is stored here.
OBSERVED_PLANS = [
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


def test_observed_stage_f2_history_has_14_plans_and_no_three_block_concentration():
    result = derive_recommendation_plan_context(OBSERVED_PLANS)

    assert result["plan_count"] == 14
    assert result["max_completed_30q_equivalent_after"] == 2
    assert max(row["consecutive_field_blocks"] for row in result["rows"]) == 1
    assert all(row["additional_blocks_completed"] is None for row in result["rows"])
    assert all(row["additional_blocks_completed_available"] is False for row in result["rows"])


def test_physiology_five_plan_streak_uses_only_prior_completed_work():
    result = derive_recommendation_plan_context(OBSERVED_PLANS)
    physiology = [row for row in result["rows"] if row["field_id"] == 2]

    assert len(physiology) == 5
    assert [row["completed_recommendation_questions"] for row in physiology] == [10, 10, 10, 20, 10]
    assert [row["observed_same_field_completed_questions_before"] for row in physiology] == [0, 10, 20, 30, 50]
    assert [row["consecutive_field_blocks"] for row in physiology] == [0, 0, 0, 1, 1]
    assert physiology[-1]["observed_same_field_completed_questions_after"] == 60
    assert physiology[-1]["completed_30q_equivalent_after"] == 2


def test_field_change_resets_observed_concentration_context():
    result = derive_recommendation_plan_context(OBSERVED_PLANS)
    rows = result["rows"]

    # Physiology ends at plan index 8. The next plan is neurology, so its
    # pre-plan concentration context must reset to zero even though 60 questions
    # were completed across the prior physiology recommendation streak.
    assert rows[8]["field_id"] == 2
    assert rows[8]["observed_same_field_completed_questions_after"] == 60
    assert rows[9]["field_id"] == 9
    assert rows[9]["consecutive_field_blocks"] == 0
    assert rows[9]["observed_same_field_completed_questions_before"] == 0
