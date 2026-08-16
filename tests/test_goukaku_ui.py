import os

os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ.setdefault("CHANNEL_ACCESS_TOKEN", "test-token")
os.environ.setdefault("CHANNEL_SECRET", "test-secret")

from app import app
import database
from database import record_learning_batch
from goukaku_ui import create_dashboard_token
from question_bank import CATEGORY_NAMES, get_category_small


def test_goukaku_home_renders():
    response = app.test_client().get("/goukaku-no-michi")
    assert response.status_code == 200
    text = response.get_data(as_text=True)
    assert "合格への道" in text
    assert "総合到達度" in text
    assert "すべて見る" in text
    assert "学習時間" in text
    assert "今日のおすすめ学習" in text
    assert "今日の目標" in text
    assert "（暫定）" in text
    assert "まだデータがありません。勉強するとここに表示されます＾＾" in text
    assert "2027/02/20" in text
    assert ">0<small>問</small>" in text
    assert "data-line-message=\"相談する\"" in text
    assert 'class="app-shell"' in text
    assert "20260812-pc1" in text
    assert 'class="page-content dashboard-grid"' in text


def test_goukaku_subjects_renders_official_tab_label():
    response = app.test_client().get("/goukaku-no-michi/subjects")
    assert response.status_code == 200
    text = response.get_data(as_text=True)
    assert "分野別 詳細" in text
    assert "1週間の推移" in text
    assert "経過の推移" not in text
    assert "理学療法治療各論" in text
    assert 'data-metric=' not in text
    assert "現在 90問" not in text
    assert "今週のおすすめ学習" not in text
    assert "学習時間" not in text
    assert text.count("未学習") == 18
    assert "data-close" in text


def test_dashboard_and_subjects_render_real_field_history_without_demo_values():
    database._local_learning_events.clear()
    user_id = "field-ui-user"
    q_id = "Q1"
    category_name = CATEGORY_NAMES[get_category_small(q_id)]
    record_learning_batch(
        user_id, "field-ui-event", "study", 2, 1,
        question_results=[
            {"question_id": q_id, "selected_answers": ["1"], "is_correct": True, "confidence": 1},
            {"question_id": q_id, "selected_answers": ["2"], "is_correct": False, "confidence": 2},
        ],
    )
    token = create_dashboard_token(user_id)
    client = app.test_client()

    home_text = client.get(f"/goukaku-no-michi?token={token}").get_data(as_text=True)
    assert category_name in home_text
    assert "2問" in home_text
    assert "50%" in home_text
    assert f"/goukaku-no-michi/subjects?token={token}" in home_text

    detail_text = client.get(f"/goukaku-no-michi/subjects?token={token}").get_data(as_text=True)
    assert all(name in detail_text for name in CATEGORY_NAMES.values())
    assert category_name in detail_text
    assert "2問" in detail_text
    assert "50%" in detail_text
    assert "データがありません" not in detail_text
    assert "126問" not in detail_text
    assert "184分" not in detail_text
    database._local_learning_events.clear()


def test_footprints_use_registered_name_parameter():
    response = app.test_client().get("/goukaku-no-michi/footprints?name=たろう")
    assert response.status_code == 200
    text = response.get_data(as_text=True)
    assert "たろうの足跡" in text
    assert "相談内容は表示せず" in text


def test_learning_selection_shows_selected_field():
    response = app.test_client().get("/goukaku-no-michi/learning?field=精神医学&count=10")
    assert response.status_code == 200
    text = response.get_data(as_text=True)
    assert "選択した分野" in text
    assert "精神医学" in text
    assert "10問" in text
    assert "この分野の学習へ進む" in text


def test_mode_intro_copy_is_kept_verbatim():
    from app import CONSULTATION_INTRO, NEKKETSU_INTRO

    assert "なんだ、今日は何があった？話してみな。" in CONSULTATION_INTRO
    assert "さぁ、今日はどれで暴れる？ｗ" in NEKKETSU_INTRO
