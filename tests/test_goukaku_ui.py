import os
from types import SimpleNamespace

os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ.setdefault("CHANNEL_ACCESS_TOKEN", "test-token")
os.environ.setdefault("CHANNEL_SECRET", "test-secret")

import app as app_module
from app import app
import database
from database import record_learning_batch
from goukaku_ui import create_dashboard_token
from question_bank import CATEGORY_NAMES, get_category_small


def test_goukaku_home_renders(monkeypatch):
    monkeypatch.setenv("LINE_OFFICIAL_ACCOUNT_ID", "@licensetown-test")
    monkeypatch.setenv("LIFF_ID", "1234567890-test")
    response = app.test_client().get("/goukaku-no-michi")
    assert response.status_code == 200
    text = response.get_data(as_text=True)
    assert "合格への道" in text
    assert "総合到達度" in text
    assert "すべて見る" in text
    assert "学習時間" in text
    assert "累計学習時間" in text
    assert "源さんの一言" in text
    assert "images/characters/gensan_main.png" in text
    assert 'class="app-header title-only"' in text
    assert "data-close" not in text
    assert "今日のおすすめ学習" in text
    assert "（暫定）" in text
    assert "まだデータがありません。勉強するとここに表示されます＾＾" in text
    assert "2027/02/20" in text
    assert ">0<small>問</small>" in text
    assert "data-line-message=\"相談する\"" in text
    assert 'class="app-shell"' in text
    assert text.count("20260830-recommend-pc1") == 2
    assert 'data-line-account-id="@licensetown-test"' in text
    assert 'data-liff-id="1234567890-test"' in text
    assert "https://static.line-scdn.net/liff/edge/2/sdk.js" in text
    assert 'class="page-content dashboard-grid"' in text
    assert app.test_client().get("/static/images/characters/gensan_main.png").status_code == 200
    assert 'class="summary-grid five"' in text
    assert "連続学習日数" in text
    assert 'class="learning-overview"' in text
    assert 'class="guidance-stack"' in text
    assert 'class="motivation-grid dashboard-footer-cards"' in text
    guidance_labels = ["苦手分野 TOP3", "今日のおすすめ学習", "源さんの一言"]
    assert [text.index(label) for label in guidance_labels] == sorted(text.index(label) for label in guidance_labels)
    assert text.index("分野別 到達度") < text.index("次の報酬まで")
    assert text.index("源さんの一言") < text.index("次の報酬まで")
    assert 'class="motivation-card target-progress-card"' in text
    assert text.count("目標学習量まで") >= 2
    assert "あと <b>100</b>%" in text
    assert 'class="target-progress"' in text
    assert "あと 96%" not in (__import__("pathlib").Path(__file__).resolve().parents[1] / "templates" / "goukaku" / "home.html").read_text(encoding="utf-8")
    template = (__import__("pathlib").Path(__file__).resolve().parents[1] / "templates" / "goukaku" / "home.html").read_text(encoding="utf-8")
    assert "回答数が少ないため、まだ実力判定できません" in template
    assert "{{ dashboard.recommendation_reason }}" in template


def test_dashboard_responsive_css_hides_actions_only_on_pc():
    css = (__import__("pathlib").Path(__file__).resolve().parents[1] / "static" / "goukaku" / "goukaku.css").read_text(encoding="utf-8")
    assert "@media(min-width:701px){.mobile-actions{display:none!important}" in css
    assert "@media(max-width:700px)" in css
    assert ".motivation-grid{display:grid;grid-template-columns:repeat(4" in css
    assert ".dashboard-grid .summary-grid .mini-card strong{font-size:35px}" in css
    assert ".countdown strong{display:flex;align-items:baseline;white-space:nowrap}" in css
    assert ".gensan-card img{width:120px;height:120px}" in css
    assert ".subject-card>.subject-list>.empty-state{display:flex;min-height:150px" in css
    assert ".detail-page .detail-row{grid-template-columns:198px 1fr 62px 16px;height:66px" in css
    assert ".detail-page .detail-row .bar{height:12px}" in css
    assert ".combo-chart{height:295px" in css
    assert ".chart-item small{width:58px;min-height:32px;font-size:10px" in css
    assert ".subject-chart{height:300px" in css
    assert ".daily-chart{height:280px" in css
    assert ".chart-empty{min-height:150px" in css
    assert ".learning-overview{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr)" in css
    assert ".guidance-stack{display:grid;grid-template-rows:auto 1fr 1fr" in css
    assert ".dashboard-grid>.dashboard-footer-cards{grid-column:1/-1;grid-template-columns:repeat(2" in css
    assert ".target-progress-card{border-color:#b8e1c8}" in css
    assert ".target-progress i{display:block;height:100%" in css
    assert ".recommend-card p{font-size:15px}" in css
    assert ".daily-target,.gensan-card small{font-size:13px}" in css
    assert ".gensan-card p{white-space:pre-line}" in css
    assert ".recommend-card>strong{font-size:17px;font-weight:700}" in css
    assert ".recommend-card p{line-height:1.65}" in css
    assert ".daily-target{font-size:14px}" in css
    assert ".gensan-card p{font-size:17px;font-weight:700;line-height:1.6}" in css
    assert ".gensan-card small{font-size:14px}" in css


def test_mobile_actions_use_official_account_chat_not_line_share():
    js = (__import__("pathlib").Path(__file__).resolve().parents[1] / "static" / "goukaku" / "goukaku.js").read_text(encoding="utf-8")
    assert "https://line.me/R/oaMessage/" in js
    assert "line.me/R/msg/text" not in js
    assert "line.me/R/share" not in js
    assert "shareTargetPicker" not in js
    assert "window.liff.init({ liffId })" in js
    assert "window.liff.sendMessages([{ type: 'text', text: message }])" in js
    assert "window.liff.closeWindow()" in js
    for command in ("ホームに戻る", "勉強する", "相談する", "熱血モード"):
        assert f'data-line-message="{command}"' in app.test_client().get("/goukaku-no-michi").get_data(as_text=True)


def test_goukaku_subjects_renders_official_tab_label():
    response = app.test_client().get("/goukaku-no-michi/subjects")
    assert response.status_code == 200
    text = response.get_data(as_text=True)
    assert "分野別 詳細" in text
    assert ">グラフ<" in text
    assert "1週間の推移" not in text
    assert "経過の推移" not in text
    assert "理学療法治療各論" in text
    assert 'data-metric=' not in text
    assert "現在 90問" not in text
    assert "今週のおすすめ学習" not in text
    assert "31分/日" not in text
    assert text.count("未学習") == 18
    assert "分野別比較" in text
    assert "直近7日の推移" in text
    assert "TOP画面へ戻る" in text
    assert "data-close" not in text
    assert "まだグラフに表示できる学習データがありません。" in text
    assert "直近7日の学習データはまだありません。" in text
    assert 'data-combo-chart' not in text


def test_dashboard_and_subjects_render_real_field_history_without_demo_values(monkeypatch):
    monkeypatch.setenv("LINE_OFFICIAL_ACCOUNT_ID", "@licensetown-test")
    monkeypatch.setenv("LIFF_ID", "1234567890-test")
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
    assert "100問を目標に基礎を固めましょう" in home_text
    assert "今日は解剖学を10問解こう" in home_text
    assert "チャレンジする！" in home_text
    assert 'data-recommendation-start-url="/goukaku-no-michi/recommendation/start"' in home_text
    assert f'data-dashboard-token="{token}"' in home_text
    assert 'data-recommendation-field="解剖学"' in home_text
    assert 'data-recommendation-count="10"' in home_text
    assert 'data-line-message="今日のおすすめ学習：解剖学：10問"' not in home_text
    assert "閲覧のみ" not in home_text
    assert f"/goukaku-no-michi/subjects?token={token}" in home_text

    detail_text = client.get(f"/goukaku-no-michi/subjects?token={token}").get_data(as_text=True)
    assert all(name in detail_text for name in CATEGORY_NAMES.values())
    assert category_name in detail_text
    assert "2問" in detail_text
    assert "50%" in detail_text
    assert "まだグラフに表示できる学習データがありません。" not in detail_text
    assert 'class="combo-chart subject-chart"' in detail_text
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


def test_recommendation_challenge_has_scoped_responsive_cta_css():
    css = (__import__("pathlib").Path(__file__).resolve().parents[1] / "static" / "goukaku" / "goukaku.css").read_text(encoding="utf-8")
    assert ".recommend-card .recommend-challenge{min-height:46px" in css
    assert "@media(max-width:700px){.recommend-card .recommend-challenge{width:100%;min-height:48px" in css
    assert ".recommend-card .recommend-challenge-status{" in css


def test_dashboard_recommendation_post_uses_token_user(monkeypatch):
    token = create_dashboard_token("recommendation-token-user")
    started = []
    monkeypatch.setattr(
        app_module,
        "build_dashboard",
        lambda user_id: {"recommended_study": [("医学概論", 10)]},
    )
    monkeypatch.setattr(
        app_module,
        "start_and_push_dashboard_recommendation",
        lambda user_id, category_small, count: started.append(
            (user_id, category_small, count)
        ) or True,
    )

    response = app.test_client().post(
        "/goukaku-no-michi/recommendation/start",
        json={"token": token, "field": "医学概論", "count": 10, "user_id": "attacker"},
    )

    assert response.status_code == 200
    assert response.get_json()["message"] == "LINEに問題を送りました。"
    assert started == [("recommendation-token-user", 6, 10)]


def test_dashboard_recommendation_post_rejects_invalid_token_field_and_count(monkeypatch):
    started = []
    monkeypatch.setattr(
        app_module,
        "start_and_push_dashboard_recommendation",
        lambda *args: started.append(args),
    )
    client = app.test_client()
    token = create_dashboard_token("recommendation-validation-user")

    assert client.post(
        "/goukaku-no-michi/recommendation/start",
        json={"field": "医学概論", "count": 10},
    ).status_code == 403
    assert client.post(
        "/goukaku-no-michi/recommendation/start",
        json={"token": "invalid", "field": "医学概論", "count": 10},
    ).status_code == 403
    assert client.post(
        "/goukaku-no-michi/recommendation/start",
        json={"token": token, "field": "存在しない分野", "count": 10},
    ).status_code == 400
    assert client.post(
        "/goukaku-no-michi/recommendation/start",
        json={"token": token, "field": "医学概論", "count": 30},
    ).status_code == 400
    assert started == []


def test_dashboard_recommendation_post_rejects_stale_display(monkeypatch):
    token = create_dashboard_token("recommendation-stale-user")
    monkeypatch.setattr(
        app_module,
        "build_dashboard",
        lambda user_id: {"recommended_study": [("解剖学", 10)]},
    )

    response = app.test_client().post(
        "/goukaku-no-michi/recommendation/start",
        json={"token": token, "field": "医学概論", "count": 10},
    )

    assert response.status_code == 409


def test_dashboard_recommendation_pushes_first_set_once(monkeypatch):
    user_id = "recommendation-push-user"
    app_module.study_sessions.pop(user_id, None)
    pushes = []

    def fake_start_quiz(start_user_id, session_kind=None, question_count=None, **_kwargs):
        assert start_user_id == user_id
        app_module.study_sessions[user_id] = {
            "session_kind": session_kind,
            "category_small": 6,
            "question_count": question_count,
            "status": "waiting_for_answers",
        }

    monkeypatch.setattr(app_module, "start_quiz", fake_start_quiz)
    monkeypatch.setattr(
        app_module,
        "build_current_quiz_messages",
        lambda session, intro_text=None: ["intro", "questions-1-5", "answer-guide"],
    )
    monkeypatch.setattr(
        app_module,
        "line_bot_api",
        SimpleNamespace(push_message=lambda target, messages: pushes.append((target, messages))),
    )

    assert app_module.start_and_push_dashboard_recommendation(user_id, 6, 10) is True
    assert pushes == [(user_id, ["intro", "questions-1-5", "answer-guide"])]
    assert app_module.start_and_push_dashboard_recommendation(user_id, 6, 10) is False
    assert len(pushes) == 1
    app_module.study_sessions.pop(user_id, None)


def test_dashboard_recommendation_js_posts_without_line_redirect():
    js = (__import__("pathlib").Path(__file__).resolve().parents[1] / "static" / "goukaku" / "goukaku.js").read_text(encoding="utf-8")
    assert "fetch(button.dataset.recommendationStartUrl" in js
    assert "credentials: 'same-origin'" in js
    assert "LINEに問題を送りました。" in js
    assert "if (await liffReady) window.liff.closeWindow();" in js
    assert "[data-line-message]:not([data-recommendation-start-url])" in js


def test_mode_intro_copy_is_kept_verbatim():
    from app import CONSULTATION_INTRO, NEKKETSU_INTRO

    assert "なんだ、今日は何があった？話してみな。" in CONSULTATION_INTRO
    assert "さぁ、今日はどれで暴れる？ｗ" in NEKKETSU_INTRO
