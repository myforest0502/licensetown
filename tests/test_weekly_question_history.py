import os
from datetime import datetime, timedelta, timezone

os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ.setdefault("CHANNEL_ACCESS_TOKEN", "test-token")
os.environ.setdefault("CHANNEL_SECRET", "test-secret")

import database
from app import app
from database import get_weekly_question_history, set_supporter_link, deactivate_supporter_link
from goukaku_ui import create_supporter_token


NOW = datetime(2026, 8, 30, 3, 0, tzinfo=timezone.utc)  # 2026/08/30 JST


def row(q, days, correct, confidence=2, selected=None, user="learner"):
    return {"event_key": f"{user}-{q}-{days}-{confidence}", "user_id": user,
            "question_id": q, "knowledge_node_id": "KN0001", "mode": "study",
            "selected_answers": ["A"] if selected is None else selected,
            "is_correct": correct, "confidence": confidence,
            "answered_at": NOW - timedelta(days=days), "attempt_position": 1}


def setup_function():
    database._local_question_attempts.clear()
    database._local_supporter_links.clear()


def test_weekly_summary_boundaries_duplicates_unknown_and_natural_sort():
    database._local_question_attempts.extend([
        row("Q10", 0, False, 1), row("Q2", 1, False, 2), row("Q2", 1, True, 1),
        row("Q3", 2, False, None, []), row("Q20", 7, False, 1),
        row("Q1", 0, False, 1, user="other"),
    ])
    result = get_weekly_question_history("learner", NOW)
    assert result["start_date"].isoformat() == "2026-08-24"
    assert result["end_date"].isoformat() == "2026-08-30"
    assert result["total_attempts"] == 4
    assert result["unique_questions"] == 3
    assert result["attempted_question_ids"] == ["Q2", "Q3", "Q10"]
    assert result["wrong_question_ids"] == ["Q2", "Q3", "Q10"]
    assert result["unknown_question_ids"] == ["Q3"]
    assert result["confident_wrong_question_ids"] == ["Q10"]


def test_supporter_weekly_page_requires_signed_active_link_and_has_copy_data(monkeypatch):
    database._local_question_attempts.extend([row("Q10", 0, False, 1), row("Q2", 0, True, 1)])
    set_supporter_link("supporter", "learner")
    token = create_supporter_token("supporter")
    client = app.test_client()
    path = f"/supporter/weekly-question-history?token={token}&learner_user_id=learner"
    assert client.get("/supporter/weekly-question-history").status_code == 403
    assert client.get(
        f"/supporter/weekly-question-history?token={token}&learner_user_id=other"
    ).status_code == 403
    response = client.get(path)
    text = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "今週の学習履歴" in text
    assert 'data-copy-q-ids="Q2 Q10"' in text
    assert "Q番号をコピー" in text
    assert "問題文" not in text
    deactivate_supporter_link("supporter", "learner")
    assert client.get(path).status_code == 403


def test_copy_script_uses_space_separated_dataset():
    source = (__import__("pathlib").Path(__file__).parents[1] / "static/goukaku/goukaku.js").read_text(encoding="utf-8")
    assert "navigator.clipboard.writeText(button.dataset.copyQIds)" in source
    assert "コピーしました" in source
