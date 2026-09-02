from phase11_evaluable_nonrepair_rules import (
    build_j5_sparse_field_candidates,
    build_j6_uncertain_correct_candidates,
)


def field(
    *,
    evaluable=0,
    raw=0,
    unknown=0,
    coverage=0.0,
    checking=0,
):
    return {
        "evaluable_answer_count": evaluable,
        "question_answer_count": raw,
        "unknown_answer_count": unknown,
        "node_coverage": {"percent": coverage},
        "checking_node_count": checking,
    }


def test_j5_uses_evaluable_count_not_raw_attempt_count():
    candidates = build_j5_sparse_field_candidates({
        1: field(evaluable=0, raw=10, unknown=10, coverage=10.0),
        2: field(evaluable=10, raw=10, unknown=0, coverage=10.0),
    })
    assert [item["field_id"] for item in candidates] == [1]
    assert candidates[0]["raw_answer_count"] == 10
    assert candidates[0]["evaluable_answer_count"] == 0


def test_j5_orders_by_evaluable_then_coverage_then_field_id():
    candidates = build_j5_sparse_field_candidates({
        3: field(evaluable=4, coverage=10.0),
        2: field(evaluable=4, coverage=5.0),
        1: field(evaluable=3, coverage=50.0),
    })
    assert [item["field_id"] for item in candidates] == [1, 2, 3]


def test_j5_excludes_fields_with_ten_evaluable_answers():
    assert build_j5_sparse_field_candidates({1: field(evaluable=10)}) == []


def test_j6_unknown_attempts_do_not_satisfy_five_answer_minimum():
    candidates = build_j6_uncertain_correct_candidates(
        {1: field(evaluable=3, raw=5, unknown=2)},
        uncertain_correct_by_field={1: 3},
    )
    assert candidates == []


def test_j6_requires_three_uncertain_correct_answers():
    candidates = build_j6_uncertain_correct_candidates(
        {1: field(evaluable=10)},
        uncertain_correct_by_field={1: 2},
    )
    assert candidates == []


def test_j6_orders_count_then_evaluable_proportion_then_checking():
    candidates = build_j6_uncertain_correct_candidates(
        {
            1: field(evaluable=10, checking=1),
            2: field(evaluable=5, checking=0),
            3: field(evaluable=5, checking=3),
        },
        uncertain_correct_by_field={1: 3, 2: 3, 3: 3},
    )
    assert [item["field_id"] for item in candidates] == [3, 2, 1]
    assert candidates[0]["uncertain_correct_proportion"] == 0.6


def test_j6_field_id_is_final_tie_break():
    candidates = build_j6_uncertain_correct_candidates(
        {
            2: field(evaluable=5, checking=1),
            1: field(evaluable=5, checking=1),
        },
        uncertain_correct_by_field={1: 3, 2: 3},
    )
    assert [item["field_id"] for item in candidates] == [1, 2]
