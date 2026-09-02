from phase11_active_repair_rules import build_j2_candidates, build_j3_candidates


def active(
    *,
    cross_confident=0,
    confident_nodes=0,
    cross_wrong=0,
    repeated=0,
    repairing=0,
):
    return {
        "active_cross_question_confident_wrong_node_count": cross_confident,
        "active_confident_wrong_repairing_node_count": confident_nodes,
        "active_cross_question_wrong_node_count": cross_wrong,
        "active_repeated_weakness_node_count": repeated,
        "active_evaluable_wrong_repairing_node_count": repairing,
    }


def field(*, evaluable_count=0, evaluable_accuracy=None):
    return {
        "evaluable_answer_count": evaluable_count,
        "evaluable_accuracy": evaluable_accuracy,
    }


def test_j2_cross_confident_precedes_confident_node_cluster():
    candidates = build_j2_candidates(
        {
            1: active(cross_confident=1, confident_nodes=1, repairing=1),
            2: active(confident_nodes=3, repairing=3),
        },
        field_records={1: field(), 2: field()},
    )
    assert [item["field_id"] for item in candidates] == [1, 2]


def test_j2_uses_active_evaluable_repairing_burden_not_total_state_count():
    candidates = build_j2_candidates(
        {
            1: active(confident_nodes=2, repairing=2),
            2: active(confident_nodes=2, repairing=4),
        },
        field_records={1: field(), 2: field()},
    )
    assert [item["field_id"] for item in candidates] == [2, 1]


def test_j2_sparse_evaluable_accuracy_cannot_win():
    candidates = build_j2_candidates(
        {
            1: active(confident_nodes=2, repairing=2),
            2: active(confident_nodes=2, repairing=2),
        },
        field_records={
            1: field(evaluable_count=4, evaluable_accuracy=0.0),
            2: field(evaluable_count=10, evaluable_accuracy=0.8),
        },
    )
    assert [item["field_id"] for item in candidates] == [2, 1]
    assert candidates[1]["reliable_accuracy"] == 1.0


def test_j2_evaluable_accuracy_breaks_exact_reliable_tie():
    candidates = build_j2_candidates(
        {
            1: active(confident_nodes=2, repairing=2),
            2: active(confident_nodes=2, repairing=2),
        },
        field_records={
            1: field(evaluable_count=10, evaluable_accuracy=0.7),
            2: field(evaluable_count=10, evaluable_accuracy=0.5),
        },
    )
    assert [item["field_id"] for item in candidates] == [2, 1]


def test_j2_requires_cross_confident_or_two_confident_nodes():
    candidates = build_j2_candidates(
        {1: active(confident_nodes=1, repairing=5)},
        field_records={1: field(evaluable_count=20, evaluable_accuracy=0.2)},
    )
    assert candidates == []


def test_j3_cross_wrong_precedes_repeated_cluster():
    candidates = build_j3_candidates({
        1: active(cross_wrong=1, repeated=1, repairing=1),
        2: active(repeated=3, repairing=3),
    })
    assert [item["field_id"] for item in candidates] == [1, 2]


def test_j3_uses_active_evaluable_repairing_burden():
    candidates = build_j3_candidates({
        1: active(repeated=2, repairing=2),
        2: active(repeated=2, repairing=4),
    })
    assert [item["field_id"] for item in candidates] == [2, 1]


def test_j3_lone_repeated_node_does_not_trigger():
    candidates = build_j3_candidates({
        1: active(repeated=1, repairing=1),
    })
    assert candidates == []


def test_j3_two_repeated_nodes_trigger():
    candidates = build_j3_candidates({
        1: active(repeated=2, repairing=2),
    })
    assert [item["field_id"] for item in candidates] == [1]
