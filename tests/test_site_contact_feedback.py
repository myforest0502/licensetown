from datetime import datetime, timezone

from flask import Flask

import site_legal_ui
from feedback_store import FeedbackReceipt, FeedbackValidationError


def _app():
    app = Flask(__name__)
    app.register_blueprint(site_legal_ui.site_legal_ui)
    app.config.update(TESTING=True)
    return app


def test_contact_get_has_low_friction_fields():
    response = _app().test_client().get("/site/legal/contact")
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "お名前" in html
    assert "ニックネームでも可・任意" in html
    assert "返信先メールアドレス" in html
    assert "未入力でも送信できます" in html
    assert "不具合" in html
    assert "ご要望" in html
    assert "使い方について" in html
    assert "お問い合わせ内容" in html
    assert "販売開始前の準備ページ" not in html


def test_contact_post_success_shows_receipt_and_private_status_link(monkeypatch):
    receipt = FeedbackReceipt(
        public_id="LT-20260906-ABCDEF12",
        tracking_token="private-token-123",
        created_at=datetime.now(timezone.utc),
    )
    calls = []

    def fake_create_feedback(**kwargs):
        calls.append(kwargs)
        return receipt

    monkeypatch.setattr(site_legal_ui, "create_feedback", fake_create_feedback)
    response = _app().test_client().post(
        "/site/legal/contact",
        data={
            "name": "源さんファン",
            "email": "user@example.test",
            "category": "request",
            "message": "この機能がほしいです。",
            "website": "",
        },
    )
    assert response.status_code == 201
    html = response.get_data(as_text=True)
    assert "LT-20260906-ABCDEF12" in html
    assert "private-token-123" in html
    assert "受付番号だけでは内容を表示できません" in html
    assert calls[0]["name"] == "源さんファン"
    assert calls[0]["source"] == "web"


def test_contact_validation_error_preserves_input(monkeypatch):
    def fake_create_feedback(**kwargs):
        raise FeedbackValidationError("メールアドレスの形式を確認してください。")

    monkeypatch.setattr(site_legal_ui, "create_feedback", fake_create_feedback)
    response = _app().test_client().post(
        "/site/legal/contact",
        data={
            "name": "ニック",
            "email": "bad",
            "category": "bug",
            "message": "困っています",
        },
    )
    assert response.status_code == 400
    html = response.get_data(as_text=True)
    assert "メールアドレスの形式を確認してください" in html
    assert "ニック" in html
    assert "困っています" in html


def test_honeypot_submission_does_not_write(monkeypatch):
    def should_not_run(**kwargs):
        raise AssertionError("honeypot submission must not be stored")

    monkeypatch.setattr(site_legal_ui, "create_feedback", should_not_run)
    response = _app().test_client().post(
        "/site/legal/contact",
        data={
            "website": "https://spam.example",
            "category": "other",
            "message": "spam",
        },
    )
    assert response.status_code == 200
    assert "お問い合わせを受け付けました" in response.get_data(as_text=True)


def test_status_page_shows_reply_but_not_private_submission(monkeypatch):
    monkeypatch.setattr(
        site_legal_ui,
        "get_feedback_for_public_status",
        lambda token: {
            "public_id": "LT-20260906-ABCDEF12",
            "category": "bug",
            "status": "responded",
            "operator_reply": "ご報告ありがとうございます。修正しました。",
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "replied_at": datetime.now(timezone.utc),
        },
    )
    response = _app().test_client().get("/site/legal/contact/status?token=secret")
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "返信済み" in html
    assert "ご報告ありがとうございます。修正しました。" in html
    assert "お名前・メールアドレス・送信本文は表示しません" in html


def test_status_page_without_private_token_does_not_enumerate_by_receipt():
    response = _app().test_client().get("/site/legal/contact/status")
    assert response.status_code == 400
    html = response.get_data(as_text=True)
    assert "専用の確認URL" in html
