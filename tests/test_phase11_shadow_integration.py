import copy
import os

os.environ.setdefault("OPENAI_API_KEY", "x")
os.environ.setdefault("CHANNEL_ACCESS_TOKEN", "x")
os.environ.setdefault("CHANNEL_SECRET", "x")

import database
from app import app


def setup_function():
    database._local_learning_events.clear()
    database._local_question_attempts.clear()
    database._local_user_node_states.clear()
    database._local_supporter_links.clear()


def test_shadow_diagnostics_is_internal_only_and_read_only(monkeypatch):
    monkeypatch.setenv("LT_INTERNAL_ADMIN_TOKEN", "admin-secret")
    before_events = copy.deepcopy(database._local_learning_events)
    before_attempts = copy.deepcopy(database._local_question_attempts)
    before_states = copy.deepcopy(database._local_user_node_states)

    client = app.test_client()
    response = client.get(
        "/internal/pilot-diagnostics?token=admin-secret&learner_user_id=learner&period=7"
    )
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "⑪ Shadow判断（開発中）" in html
    assert "この判断は学習者画面には反映されていません。" in html
    assert "Shadow intent" in html
    assert "現行おすすめ" in html
    assert "現行比較" in html

    assert database._local_learning_events == before_events
    assert database._local_question_attempts == before_attempts
    assert database._local_user_node_states == before_states

    learner_html = client.get("/goukaku-no-michi?token=invalid").get_data(as_text=True)
    assert "⑪ Shadow判断（開発中）" not in learner_html
    assert "Shadow intent" not in learner_html
