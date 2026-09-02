from phase11_retrospective_shadow_audit import _ordinary_single_wrong_takeover_candidate


def test_valid_two_node_confident_wrong_cluster_is_not_flagged():
    assert _ordinary_single_wrong_takeover_candidate(
        {"reason_code": "confident_wrong_cluster"},
        {
            "active_cross_question_confident_wrong_node_count": 0,
            "active_confident_wrong_repairing_node_count": 2,
        },
    ) is False


def test_valid_cross_question_confident_wrong_cluster_is_not_flagged():
    assert _ordinary_single_wrong_takeover_candidate(
        {"reason_code": "confident_wrong_cluster"},
        {
            "active_cross_question_confident_wrong_node_count": 1,
            "active_confident_wrong_repairing_node_count": 1,
        },
    ) is False


def test_invalid_j2_without_formal_trigger_is_flagged():
    assert _ordinary_single_wrong_takeover_candidate(
        {"reason_code": "confident_wrong_cluster"},
        {
            "active_cross_question_confident_wrong_node_count": 0,
            "active_confident_wrong_repairing_node_count": 1,
        },
    ) is True


def test_valid_repeated_wrong_cluster_is_not_flagged():
    assert _ordinary_single_wrong_takeover_candidate(
        {"reason_code": "repeated_wrong_cluster"},
        {
            "active_cross_question_wrong_node_count": 0,
            "active_repeated_weakness_node_count": 2,
        },
    ) is False


def test_valid_cross_question_wrong_cluster_is_not_flagged():
    assert _ordinary_single_wrong_takeover_candidate(
        {"reason_code": "repeated_wrong_cluster"},
        {
            "active_cross_question_wrong_node_count": 1,
            "active_repeated_weakness_node_count": 0,
        },
    ) is False


def test_invalid_j3_without_formal_trigger_is_flagged():
    assert _ordinary_single_wrong_takeover_candidate(
        {"reason_code": "repeated_wrong_cluster"},
        {
            "active_cross_question_wrong_node_count": 0,
            "active_repeated_weakness_node_count": 1,
        },
    ) is True


def test_non_j2_j3_reason_is_never_flagged():
    assert _ordinary_single_wrong_takeover_candidate(
        {"reason_code": "insufficient_coverage"},
        {},
    ) is False
