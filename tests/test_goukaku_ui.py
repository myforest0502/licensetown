import os

os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ.setdefault("CHANNEL_ACCESS_TOKEN", "test-token")
os.environ.setdefault("CHANNEL_SECRET", "test-secret")

import app as app_module
from app import app
import database
from database import record_learning_batch
import goukaku_ui as goukaku_ui_module
from goukaku_ui import build_dashboard, create_dashboard_token
from question_bank import CATEGORY_NAMES, get_category_small, get_quiz_question, question_ids


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
    assert "おすすめ進捗" not in text
    assert "（暫定）" in text
    assert "まだデータがありません。勉強するとここに表示されます＾＾" in text
    assert "2027/02/20" in text
    assert ">0<small>問</small>" in text
    assert "data-line-message=\"相談する\"" in text
    assert 'class="app-shell"' in text
    assert "20260830-fixed-demo-cleanup1" in text
    assert "20260830-weekly-history1" in text
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
    assert 'data-recommendation-line-command="今日のおすすめ学習：解剖学：10問"' in home_text
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


def test_recommendation_progress_uses_recommended_field_today_count(monkeypatch):
    fields = [
        {"name": "人間発達学", "learned": True, "today_answered_count": 3},
        {"name": "解剖学", "learned": True, "today_answered_count": 5},
    ]
    monkeypatch.setattr(
        goukaku_ui_module,
        "get_dashboard_learning_data",
        lambda user_id: {
            "summary": {},
            "activity": {},
            "unique_question_count": 0,
            "fields": fields,
        },
    )
    monkeypatch.setattr(
        goukaku_ui_module,
        "build_learning_guidance",
        lambda total_answers, field_data: {
            "recommended_study": [("人間発達学", 10)],
            "recommendation_reason": "test",
            "weak_fields": [],
        },
    )
    monkeypatch.setattr(goukaku_ui_module, "build_gensan_comment", lambda *args: "test")

    dashboard = build_dashboard("recommendation-progress-user")

    assert dashboard["recommendation_progress"] == 3
    assert dashboard["recommendation_goal"] == 10
    assert "today_goal" in dashboard
    assert "today_progress" in dashboard


def test_recommendation_progress_is_capped_and_ignores_other_fields(monkeypatch):
    def dashboard_for(recommended_count, other_count=0):
        fields = [
            {"name": "人間発達学", "learned": True, "today_answered_count": recommended_count},
            {"name": "解剖学", "learned": True, "today_answered_count": other_count},
        ]
        monkeypatch.setattr(
            goukaku_ui_module,
            "get_dashboard_learning_data",
            lambda user_id: {
                "summary": {},
                "activity": {},
                "unique_question_count": 0,
                "fields": fields,
            },
        )
        monkeypatch.setattr(
            goukaku_ui_module,
            "build_learning_guidance",
            lambda total_answers, field_data: {
                "recommended_study": [("人間発達学", 10)],
                "recommendation_reason": "test",
                "weak_fields": [],
            },
        )
        monkeypatch.setattr(goukaku_ui_module, "build_gensan_comment", lambda *args: "test")
        return build_dashboard("recommendation-progress-user")

    assert dashboard_for(0, other_count=5)["recommendation_progress"] == 0
    assert dashboard_for(10)["recommendation_progress"] == 10
    assert dashboard_for(15)["recommendation_progress"] == 10


def test_recommendation_card_renders_recommendation_goal_not_daily_goal(monkeypatch):
    dashboard = build_dashboard()
    dashboard.update({
        "recommended_study": [("人間発達学", 10)],
        "recommendation_reason": "test",
        "recommendation_progress": 0,
        "recommendation_goal": 10,
    })
    monkeypatch.setattr(
        goukaku_ui_module,
        "build_dashboard",
        lambda user_id: dashboard,
    )

    text = app.test_client().get("/goukaku-no-michi").get_data(as_text=True)

    assert "おすすめ進捗 0 / 10問" in text
    assert "今日の進捗" not in text
    assert "/ 30問" not in text


def test_footprints_show_safe_empty_state_without_demo_events():
    response = app.test_client().get("/goukaku-no-michi/footprints?name=たろう")
    assert response.status_code == 200
    text = response.get_data(as_text=True)
    assert "あなたの足跡" in text
    assert "学習を始めると、ここにあなたの歩みが残っていきます。" in text
    assert "トータル100問達成" not in text
    assert "初めて相談モード" not in text


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


def test_dashboard_recommendation_post_uses_token_user_and_starts_web(monkeypatch):
    token = create_dashboard_token("recommendation-token-user")
    app_module.web_recommendation_sessions.clear()
    monkeypatch.setattr(
        app_module,
        "build_dashboard",
        lambda user_id: {"recommended_study": [("医学概論", 10)]},
    )

    response = app.test_client().post(
        "/goukaku-no-michi/recommendation/start",
        json={"token": token, "field": "医学概論", "count": 10, "user_id": "attacker"},
    )

    assert response.status_code == 200
    redirect_url = response.get_json()["redirect_url"]
    assert redirect_url.startswith("/goukaku-no-michi/learning/")
    session = next(iter(app_module.web_recommendation_sessions.values()))
    assert session["user_id"] == "recommendation-token-user"
    assert session["category_small"] == 6
    assert session["question_count"] == 10
    assert len(session["questions"]) == 10
    assert app.test_client().get(redirect_url).status_code == 200

    duplicate = app.test_client().post(
        "/goukaku-no-michi/recommendation/start",
        json={"token": token, "field": "医学概論", "count": 10},
    )
    assert duplicate.status_code == 200
    assert duplicate.get_json()["redirect_url"] == redirect_url
    assert duplicate.get_json()["already_started"] is True
    assert len(app_module.web_recommendation_sessions) == 1
    app_module.web_recommendation_sessions.clear()


def test_dashboard_recommendation_post_rejects_invalid_token_field_and_count(monkeypatch):
    app_module.web_recommendation_sessions.clear()
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
    assert app_module.web_recommendation_sessions == {}


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


def test_web_recommendation_answers_unknown_multiple_and_completes(monkeypatch):
    database._local_learning_events.clear()
    database._local_question_attempts.clear()
    app_module.web_recommendation_sessions.clear()
    multi_question = next(
        question for question in (get_quiz_question(q_id) for q_id in question_ids())
        if len(question["accepted_answer_sets"][0]) > 1
    )
    questions = [multi_question] + [get_quiz_question(f"Q{number}") for number in range(1, 10)]
    session_id = "web-complete-session"
    app_module.web_recommendation_sessions[session_id] = {
        "user_id": "web-learning-user",
        "dashboard_token": create_dashboard_token("web-learning-user"),
        "category_small": 1,
        "question_count": 10,
        "questions": questions,
        "current_index": 0,
        "correct_count": 0,
        "completed": False,
        "started_at": __import__("time").time(),
    }
    client = app.test_client()

    for index, question in enumerate(questions):
        if index == 1:
            payload = {
                "question_id": str(question["id"]),
                "selected_answers": [],
                "confidence": None,
                "unknown": True,
            }
        else:
            payload = {
                "question_id": str(question["id"]),
                "selected_answers": question["accepted_answer_sets"][0],
                "confidence": 1,
                "unknown": False,
            }
        response = client.post(
            f"/goukaku-no-michi/learning/{session_id}/answer", json=payload
        )
        assert response.status_code == 200
        if index == 0:
            assert response.get_json()["is_correct"] is True

    assert app_module.web_recommendation_sessions[session_id]["completed"] is True
    assert len(database._local_learning_events) == 10
    unknown_event = next(
        event for event in database._local_learning_events.values()
        if event["question_results"][0]["answer_status"] == "unknown"
    )
    assert unknown_event["question_results"][0]["selected_answers"] == []
    assert unknown_event["question_results"][0]["confidence"] is None
    assert unknown_event["question_results"][0]["learning_source"] == "dashboard_recommendation"
    complete_text = client.get(
        f"/goukaku-no-michi/learning/{session_id}"
    ).get_data(as_text=True)
    assert "10問完走！" in complete_text
    assert "学習履歴へ保存しました" in complete_text
    app_module.web_recommendation_sessions.clear()
    database._local_learning_events.clear()
    database._local_question_attempts.clear()


def test_dashboard_recommendation_js_uses_liff_reply_or_web_without_push():
    js = (__import__("pathlib").Path(__file__).resolve().parents[1] / "static" / "goukaku" / "goukaku.js").read_text(encoding="utf-8")
    assert "fetch(button.dataset.recommendationStartUrl" in js
    assert "credentials: 'same-origin'" in js
    assert "text: button.dataset.recommendationLineCommand" in js
    assert "window.liff.sendMessages" in js
    assert "window.location.assign(result.redirect_url)" in js
    assert "[data-line-message]:not([data-recommendation-start-url])" in js
    endpoint_source = __import__("inspect").getsource(app_module.start_dashboard_recommendation)
    assert "push_message" not in endpoint_source


def test_mode_intro_copy_is_kept_verbatim():
    from app import CONSULTATION_INTRO, NEKKETSU_INTRO

    assert "なんだ、今日は何があった？話してみな。" in CONSULTATION_INTRO
    assert "さぁ、今日はどれで暴れる？ｗ" in NEKKETSU_INTRO
