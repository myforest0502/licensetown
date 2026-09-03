import dashboard_real_data_shadow as shadow


def _coverage_inputs():
    evidence = {
        "fields": [
            {"field_id": 1, "field_name": "F1", "evaluable_answer_count": 20},
            {"field_id": 2, "field_name": "F2", "evaluable_answer_count": 20},
            {"field_id": 3, "field_name": "F3", "evaluable_answer_count": 0},
            {"field_id": 4, "field_name": "F4", "evaluable_answer_count": 2},
        ]
    }
    progress = {
        "fields": [
            {"field_id": 1, "field_progress_score": 0.20, "field_progress_percent": 20.0, "node_coverage": 0.50},
            {"field_id": 2, "field_progress_score": 0.25, "field_progress_percent": 25.0, "node_coverage": 0.40},
            {"field_id": 3, "field_progress_score": 0.00, "field_progress_percent": 0.0, "node_coverage": 0.00},
            {"field_id": 4, "field_progress_score": 0.05, "field_progress_percent": 5.0, "node_coverage": 0.10},
        ]
    }
    return evidence, progress


def test_two_proven_priorities_are_filled_with_lowest_coverage_third():
    evidence, progress = _coverage_inputs()
    proven = [
        {
            "field_id": 1,
            "field_name": "F1",
            "reason_code": "repeated_wrong_repair",
            "bucket": 3,
            "severity_count": 2,
            "field_progress_score": 0.20,
            "node_coverage": 0.50,
            "is_proven_weakness": True,
        },
        {
            "field_id": 2,
            "field_name": "F2",
            "reason_code": "repairing_continue",
            "bucket": 4,
            "severity_count": 1,
            "field_progress_score": 0.25,
            "node_coverage": 0.40,
            "is_proven_weakness": True,
        },
    ]

    result = shadow._priority_top3(proven, evidence, progress)

    assert len(result) == 3
    assert [item["field_id"] for item in result] == [1, 2, 3]
    assert result[2]["reason_code"] == "coverage_expand"
    assert result[2]["is_proven_weakness"] is False
    assert len({item["field_id"] for item in result}) == 3


def test_three_proven_priorities_are_not_displaced_by_coverage():
    evidence, progress = _coverage_inputs()
    proven = [
        {"field_id": 1, "field_name": "F1", "reason_code": "safety_repair", "bucket": 1, "severity_count": 1, "field_progress_score": 0.20, "node_coverage": 0.50},
        {"field_id": 2, "field_name": "F2", "reason_code": "confident_wrong_repair", "bucket": 2, "severity_count": 1, "field_progress_score": 0.25, "node_coverage": 0.40},
        {"field_id": 4, "field_name": "F4", "reason_code": "retention_recheck", "bucket": 5, "severity_count": 1, "field_progress_score": 0.05, "node_coverage": 0.10},
    ]

    result = shadow._priority_top3(proven, evidence, progress)

    assert [item["field_id"] for item in result] == [1, 2, 4]
