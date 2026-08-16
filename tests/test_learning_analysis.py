from datetime import datetime, timezone
from pathlib import Path

import database
from database import get_field_learning_summary, get_learning_summary, record_learning_batch
from learning_analysis import build_learning_guidance
from question_bank import CATEGORY_NAMES


def make_fields(values=None):
    values = values or {}
    fields = []
    for number, name in CATEGORY_NAMES.items():
        answered, correct = values.get(number, (0, 0))
        fields.append({
            "category_small": number,
            "name": name,
            "answered_count": answered,
            "correct_count": correct,
            "accuracy": round(correct / answered * 100) if answered else None,
            "recent_7d_answered_count": 0,
            "recent_7d_correct_count": 0,
            "recent_7d_accuracy": None,
            "today_answered_count": 0,
            "today_correct_count": 0,
            "today_accuracy": None,
            "learned": answered > 0,
        })
    return fields


def test_zero_and_99_answers_stay_in_foundation_and_recommend_basic():
    for total in (0, 99):
        guidance = build_learning_guidance(total, make_fields())
        assert guidance["phase"] == "foundation"
        assert guidance["weak_fields"] == []
        assert guidance["recommended_study"] == [("解剖学", 10)]
        assert "100問" in guidance["weak_analysis_message"]


def test_foundation_recommendation_balances_unlearned_then_low_volume():
    guidance = build_learning_guidance(
        40,
        make_fields({1: (10, 8), 2: (2, 0), 3: (2, 2), 4: (1, 0), 5: (0, 0), 6: (3, 2)}),
    )
    assert guidance["recommended_study"] == [("教育学", 10)]

    guidance = build_learning_guidance(
        99,
        make_fields({1: (6, 5), 2: (2, 0), 3: (2, 2), 4: (4, 3), 5: (3, 2), 6: (5, 4)}),
    )
    assert guidance["recommended_study"] == [("生理学", 10)]

    guidance = build_learning_guidance(
        99,
        make_fields({1: (5, 4), 2: (5, 1), 3: (5, 3), 4: (5, 4), 5: (5, 4), 6: (5, 4)}),
    )
    assert guidance["recommended_study"] == [("生理学", 10)]


def test_exactly_100_starts_analysis_but_does_not_invent_three_fields():
    guidance = build_learning_guidance(100, make_fields({1: (1, 0)}))
    assert guidance["phase"] == "analysis"
    assert guidance["weak_fields"] == []
    assert guidance["recommended_study"] == []


def test_one_wrong_answer_is_not_overweighted():
    fields = make_fields({1: (1, 0), 7: (20, 4), 8: (20, 16), 9: (20, 17)})
    guidance = build_learning_guidance(100, fields)
    assert guidance["weak_fields"][0]["name"] == "病理学"
    assert all(item["name"] != "解剖学" for item in guidance["weak_fields"])


def test_reliable_low_accuracy_and_relative_deficit_rank_first_and_drive_recommendation():
    fields = make_fields({
        1: (15, 12), 2: (15, 13), 3: (15, 12), 4: (15, 13),
        7: (20, 6), 8: (20, 16),
    })
    guidance = build_learning_guidance(100, fields)
    top = guidance["weak_fields"][0]
    assert top["name"] == "病理学"
    assert top["reason"] in {"正答率が低い", "他分野より正答率が低い"}
    assert guidance["recommended_study"] == [("病理学", 10)]


def test_unlearned_is_one_candidate_only_after_broad_learning():
    fields = make_fields({number: (10, 8) for number in range(1, 7)})
    guidance = build_learning_guidance(100, fields)
    unlearned = [item for item in guidance["weak_fields"] if item["reason"] == "未学習"]
    assert len(unlearned) == 1
    assert unlearned[0]["name"] == "病理学"


def test_low_engagement_is_a_candidate_after_broad_learning():
    fields = make_fields({
        1: (15, 13), 2: (15, 13), 3: (15, 13),
        4: (15, 13), 5: (15, 13), 6: (1, 1),
    })
    guidance = build_learning_guidance(100, fields)
    low_engagement = [
        item for item in guidance["weak_fields"]
        if item["reason"] == "取り組み不足"
    ]
    assert low_engagement
    assert low_engagement[0]["name"] == "医学概論"


def test_null_legacy_history_counts_for_100_but_not_field_analysis():
    database._local_learning_events.clear()
    user_id = "legacy-analysis-user"
    record_learning_batch(
        user_id, "legacy-analysis", "study", 100, 70,
        datetime.now(timezone.utc), question_results=None,
    )
    total = get_learning_summary(user_id)["total_answers"]
    fields = get_field_learning_summary(user_id)
    guidance = build_learning_guidance(total, fields)
    assert total == 100
    assert all(item["answered_count"] == 0 for item in fields)
    assert guidance["phase"] == "analysis"
    assert guidance["weak_fields"] == []
    database._local_learning_events.clear()


def test_analysis_module_has_no_openai_dependency():
    source = Path(__import__("learning_analysis").__file__).read_text(encoding="utf-8").lower()
    assert "openai" not in source


def test_dashboard_and_supporter_use_the_same_guidance(monkeypatch):
    import goukaku_ui
    import supporter_report

    fields = make_fields({
        1: (20, 16), 2: (20, 15), 7: (20, 5),
        8: (20, 16), 9: (20, 17), 10: (20, 16),
    })
    summary = {
        "total_answers": 120,
        "correct_answers": 85,
        "average_accuracy": 71,
        "last_7_days_accuracy": 71,
        "today_progress": 0,
        "study_minutes": 0,
    }
    activity = {
        "daily": [{"answered_count": 0, "correct_count": 0, "accuracy": 0, "study_minutes": 0}],
        "streak_days": 0,
        "weekly_study_minutes": 0,
        "average_daily_study_minutes": 0,
        "weekly_learning_days": 0,
        "weekly_answers": 0,
        "weekly_correct": 0,
        "weekly_accuracy": 0,
    }
    for module in (goukaku_ui, supporter_report):
        monkeypatch.setattr(module, "get_learning_summary", lambda _user_id: summary)
        monkeypatch.setattr(module, "get_field_learning_summary", lambda _user_id: fields)
        monkeypatch.setattr(module, "get_learning_activity", lambda _user_id: activity)

    dashboard = goukaku_ui.build_dashboard("same-user")
    supporter = supporter_report.build_supporter_report("same-user")
    assert dashboard["weak_fields"] == supporter["weak_fields"]
    assert dashboard["recommended_study"] == supporter["recommended_study"]
