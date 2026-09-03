from copy import deepcopy

from adaptive_source_mix import build_source_mix_audit


TAGS = {
    "Q1": {"source": "original"},
    "Q2": {"source": "past_exam"},
    "Q3": {"source": "past_exam"},
    "Q4": {"source": "original"},
}


def _tags(question_id):
    return TAGS[question_id]


def test_source_mix_preserves_input_and_splits_route_group_accuracy_confidence():
    rows = [
        {"question_id": "Q1", "learning_source": "adaptive_daily", "selection_group": "repair", "answer_status": "answered", "is_correct": True, "confidence": 1},
        {"question_id": "Q2", "learning_source": "adaptive_daily", "selection_group": "repair", "answer_status": "answered", "is_correct": False, "confidence": 3},
        {"question_id": "Q3", "learning_source": "dashboard_recommendation", "selection_group": "exploration", "answer_status": "answered", "is_correct": True, "confidence": 2},
        {"question_id": "Q4", "learning_source": "adaptive_daily", "selection_group": "exploration", "answer_status": "unknown", "is_correct": False, "confidence": None},
    ]
    before = deepcopy(rows)
    result = build_source_mix_audit(rows, tag_getter=_tags)
    assert rows == before
    assert result["question_count"] == 4
    assert result["past_exam_count"] == 2
    assert result["past_exam_share"] == 0.5
    assert result["by_source"]["past_exam"]["accuracy"] == 0.5
    assert result["by_source"]["past_exam"]["mean_confidence"] == 2.5
    assert result["by_source"]["original"]["answered_count"] == 1
    assert result["by_learning_source"]["dashboard_recommendation"]["past_exam"]["question_ids"] == ["Q3"]
    assert result["by_selection_group"]["repair"]["past_exam"]["accuracy"] == 0.0
    assert "must not override" in result["policy_note"]


def test_empty_and_missing_classification_are_safe():
    assert build_source_mix_audit([], tag_getter=_tags)["past_exam_share"] is None
    result = build_source_mix_audit(
        [{"question_id": "Q1", "answer_status": "answered", "is_correct": True}],
        tag_getter=_tags,
    )
    assert result["by_learning_source"]["unknown"]["original"]["question_count"] == 1
    assert result["by_selection_group"]["unclassified"]["original"]["question_count"] == 1
