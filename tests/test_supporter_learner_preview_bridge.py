import os

os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ.setdefault("CHANNEL_ACCESS_TOKEN", "test-token")
os.environ.setdefault("CHANNEL_SECRET", "test-secret")

import database
from app import app
from goukaku_ui import create_supporter_token
from supporter_learner_preview_bridge import install_supporter_learner_preview_bridge


def setup_function():
    database._local_supporter_links.clear()


def test_supporter_dashboard_gets_preview_button_and_preview_is_inert(monkeypatch):
    database._local_supporter_links[("supporter", "learner")] = True
    token = create_supporter_token("supporter")
    install_supporter_learner_preview_bridge(app)
    client = app.test_client()

    normal = client.get(
        f"/supporter/goukaku-no-michi?token={token}&learner_user_id=learner"
    )
    normal_text = normal.get_data(as_text=True)
    assert normal.status_code == 200
    assert "本人画面をプレビュー" in normal_text
    assert "閲覧専用" in normal_text

    preview = client.get(
        f"/supporter/goukaku-no-michi?token={token}&learner_user_id=learner&learner_preview=1"
    )
    preview_text = preview.get_data(as_text=True)
    assert preview.status_code == 200
    assert "合格への道（本人画面プレビュー）" in preview_text
    assert "本人画面プレビュー（操作はできません）" in preview_text
    assert "見守り画面へ戻る" in preview_text
    assert "現在地" in preview_text
    assert "今日やること" in preview_text


def test_preview_requires_valid_supporter_link():
    install_supporter_learner_preview_bridge(app)
    client = app.test_client()
    response = client.get(
        "/supporter/goukaku-no-michi?token=bad&learner_user_id=learner&learner_preview=1"
    )
    assert response.status_code == 403
