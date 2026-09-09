from datetime import datetime, timezone

from phase11_active_weakness import build_active_repair_weakness


def _attempt(question_id, node_id, minute):
    return {
        "user_id": "u1",
        "question_id": question_id,
        "knowledge_node_id": node_id,
        "is_correct": False,
        "confidence": 1,
        "answer_status": "wrong",
        "attempted_at": datetime(2026, 9, 9, 9, minute, tzinfo=timezone.utc),
    }


def test_active_weakness_groups_by_derived_evidence_node_for_cross_node_exact_repeat():
    attempts = [
        _attempt("Q1585", "KN0659", 0),
        _attempt("Q9999", "KN0659", 1),
    ]

    result = build_active_repair_weakness(
        attempts,
        as_of=datetime(2026, 9, 9, 10, 0, tzinfo=timezone.utc),
    )

    assert set(result) == {"KN0659", "KN1387"}
    assert result["KN1387"]["active_evaluable_wrong_question_ids"] == ["Q1585"]
    assert result["KN0659"]["active_evaluable_wrong_question_ids"] == ["Q9999"]
