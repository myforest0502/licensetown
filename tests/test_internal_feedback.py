import os
from datetime import datetime, timezone

os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ.setdefault("CHANNEL_ACCESS_TOKEN", "test-token")
os.environ.setdefault("CHANNEL_SECRET", "test-secret")

from app import app
import developer_ui
from email_delivery import EmailDeliveryResult


def _item(**overrides):
    now = datetime.now(timezone.utc)
    item = {
        "public_id": "LT-20260906-ABCDEF12",
        "name": "テスト利用者",
        "email": "user@example.com",
        "category": "bug",
        "message": "不具合があります。",
        "status": "received",
        "operator_reply": None,
        "email_delivery_status": "not_requested",
        "email_sent_at": None,
        "created_at": now,
        "updated_at": now,
        "replied_at": None,
        "tracking_token": "private-status-token",
    }
    item.update(overrides)
    return item


def test_internal_feedback_requires_admin_secret(monkeypatch):
    monkeypatch.setenv("LT_INTERNAL_ADMIN_TOKEN", "admin-secret")
    client = app.test_client()
    assert client.get("/internal/feedback").status_code == 403
    assert client.get("/internal/feedback?token=wrong").status_code == 403


def test_internal_feedback_lists_inquiries(monkeypatch):
    monkeypatch.setenv("LT_INTERNAL_ADMIN_TOKEN", "admin-secret")
    monkeypatch.setattr(developer_ui, "list_feedback_for_operator", lambda limit=100: [_item()])
    monkeypatch.setattr(
        developer_ui,
        "get_feedback_for_operator",
        lambda public_id: _item() if public_id else None,
    )

    response = app.test_client().get(
        "/internal/feedback?token=admin-secret&public_id=LT-20260906-ABCDEF12"
    )
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "お問い合わせ対応" in html
    assert "LT-20260906-ABCDEF12" in html
    assert "不具合があります。" in html
    assert "user@example.com" in html


def test_internal_feedback_reply_saves_then_sends_email(monkeypatch):
    monkeypatch.setenv("LT_INTERNAL_ADMIN_TOKEN", "admin-secret")
    current = _item()
    events = []

    def fake_get(public_id):
        return dict(current) if public_id else None

    def fake_set_operator_reply(*, public_id, reply, status):
        events.append(("save", public_id, reply, status))
        current.update(
            operator_reply=reply,
            status=status,
            email_delivery_status="pending",
        )
        return dict(current)

    def fake_send_feedback_reply(*, public_id, to_email, reply):
        events.append(("send", public_id, to_email, reply))
        return EmailDeliveryResult("sent", "delivered", "mail-123")

    def fake_mark_email_delivery(*, public_id, delivery_status):
        events.append(("mark", public_id, delivery_status))
        current["email_delivery_status"] = delivery_status
        return True

    monkeypatch.setattr(developer_ui, "list_feedback_for_operator", lambda limit=100: [dict(current)])
    monkeypatch.setattr(developer_ui, "get_feedback_for_operator", fake_get)
    monkeypatch.setattr(developer_ui, "set_operator_reply", fake_set_operator_reply)
    monkeypatch.setattr(developer_ui, "send_feedback_reply", fake_send_feedback_reply)
    monkeypatch.setattr(developer_ui, "mark_email_delivery", fake_mark_email_delivery)

    response = app.test_client().post(
        "/internal/feedback?token=admin-secret&public_id=LT-20260906-ABCDEF12",
        data={"action": "reply", "reply": "確認して修正しました。"},
    )
    assert response.status_code == 200
    assert events[0][0] == "save"
    assert events[1][0] == "send"
    assert events[2] == ("mark", "LT-20260906-ABCDEF12", "sent")
    html = response.get_data(as_text=True)
    assert "メール配送を確認しました" in html


def test_internal_feedback_without_email_never_calls_provider(monkeypatch):
    monkeypatch.setenv("LT_INTERNAL_ADMIN_TOKEN", "admin-secret")
    current = _item(email=None)

    monkeypatch.setattr(developer_ui, "get_feedback_for_operator", lambda public_id: dict(current))
    monkeypatch.setattr(developer_ui, "list_feedback_for_operator", lambda limit=100: [dict(current)])

    def fake_set_operator_reply(*, public_id, reply, status):
        current.update(operator_reply=reply, status=status, email_delivery_status="not_requested")
        return dict(current)

    monkeypatch.setattr(developer_ui, "set_operator_reply", fake_set_operator_reply)
    monkeypatch.setattr(
        developer_ui,
        "send_feedback_reply",
        lambda **kwargs: (_ for _ in ()).throw(AssertionError("provider must not be called")),
    )

    response = app.test_client().post(
        "/internal/feedback?token=admin-secret&public_id=LT-20260906-ABCDEF12",
        data={"action": "reply", "reply": "確認しました。"},
    )
    assert response.status_code == 200
    assert "メールアドレス未入力" in response.get_data(as_text=True)
