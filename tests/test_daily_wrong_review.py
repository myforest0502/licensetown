from datetime import date

from daily_wrong_review import build_review_block, wrong_question_ids_for_jst_day


def test_wrong_question_ids_are_unique_and_keep_later_corrected_questions():
    attempts = [
        {
            "question_id": "Q10",
            "is_correct": False,
            "answered_at": "2026-09-06T00:30:00+00:00",
        },
        {
            "question_id": "Q10",
            "is_correct": True,
            "answered_at": "2026-09-06T01:00:00+00:00",
        },
        {
            "question_id": "Q20",
            "is_correct": False,
            "answered_at": "2026-09-06T02:00:00+00:00",
        },
        {
            "question_id": "Q10",
            "is_correct": False,
            "answered_at": "2026-09-06T03:00:00+00:00",
        },
    ]

    assert wrong_question_ids_for_jst_day(
        attempts, target_date=date(2026, 9, 6)
    ) == ["Q10", "Q20"]


def test_wrong_question_ids_use_jst_calendar_boundary():
    attempts = [
        {
            "question_id": "Q1",
            "is_correct": False,
            "answered_at": "2026-09-05T14:59:59+00:00",
        },
        {
            "question_id": "Q2",
            "is_correct": False,
            "answered_at": "2026-09-05T15:00:00+00:00",
        },
        {
            "question_id": "Q3",
            "is_correct": False,
            "answered_at": "2026-09-06T14:59:59+00:00",
        },
        {
            "question_id": "Q4",
            "is_correct": False,
            "answered_at": "2026-09-06T15:00:00+00:00",
        },
    ]

    assert wrong_question_ids_for_jst_day(
        attempts, target_date=date(2026, 9, 6)
    ) == ["Q2", "Q3"]


def test_review_block_contains_answer_and_explanations_but_not_question_stem():
    question = {
        "id": "Q123",
        "question": "This stem should not be repeated.",
        "explanation": "正式な正解理由です。",
        "choice_explanations": {
            "A": "Aの解説",
            "B": "Bの解説",
        },
    }

    text = build_review_block(question, lambda _question: "B")

    assert "【Q123】" in text
    assert "正解：B" in text
    assert "正式な正解理由です。" in text
    assert "A：Aの解説" in text
    assert "B：Bの解説" in text
    assert "This stem should not be repeated." not in text
