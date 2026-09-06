import pytest

import email_delivery


def test_send_feedback_reply_requires_api_key(monkeypatch):
    monkeypatch.delenv("PRIMITIVE_API_KEY", raising=False)
    with pytest.raises(email_delivery.EmailDeliveryError, match="PRIMITIVE_API_KEY"):
        email_delivery.send_feedback_reply(
            public_id="LT-20260906-ABCDEF12",
            to_email="user@example.com",
            reply="返信です。",
        )


def test_send_feedback_reply_uses_idempotency_and_maps_delivered(monkeypatch):
    monkeypatch.setenv("PRIMITIVE_API_KEY", "prim_test_secret")
    captured = {}

    class Response:
        status_code = 200

        @staticmethod
        def json():
            return {
                "data": {
                    "id": "mail-123",
                    "status": "delivered",
                    "delivery_status": "delivered",
                }
            }

    def fake_post(url, *, json, headers, timeout):
        captured.update(url=url, json=json, headers=headers, timeout=timeout)
        return Response()

    monkeypatch.setattr(email_delivery.requests, "post", fake_post)
    result = email_delivery.send_feedback_reply(
        public_id="LT-20260906-ABCDEF12",
        to_email="user@example.com",
        reply="確認しました。",
    )

    assert result.delivery_state == "sent"
    assert result.provider_status == "delivered"
    assert result.provider_message_id == "mail-123"
    assert captured["url"].endswith("/v1/send-mail")
    assert captured["json"]["to"] == "user@example.com"
    assert captured["json"]["wait"] is True
    assert "確認しました。" in captured["json"]["body_text"]
    assert "迷惑メールではない" in captured["json"]["body_text"]
    assert captured["headers"]["Authorization"] == "Bearer prim_test_secret"
    assert captured["headers"]["Idempotency-Key"].startswith(
        "lt-feedback-LT-20260906-ABCDEF12-"
    )


def test_send_feedback_reply_maps_wait_timeout_to_pending(monkeypatch):
    monkeypatch.setenv("PRIMITIVE_API_KEY", "prim_test_secret")

    class Response:
        status_code = 200

        @staticmethod
        def json():
            return {"data": {"id": "mail-456", "status": "wait_timeout"}}

    monkeypatch.setattr(
        email_delivery.requests,
        "post",
        lambda *args, **kwargs: Response(),
    )
    result = email_delivery.send_feedback_reply(
        public_id="LT-20260906-ABCDEF12",
        to_email="user@example.com",
        reply="返信です。",
    )
    assert result.delivery_state == "pending"
    assert result.provider_status == "wait_timeout"


def test_send_feedback_reply_raises_on_provider_rejection(monkeypatch):
    monkeypatch.setenv("PRIMITIVE_API_KEY", "prim_test_secret")

    class Response:
        status_code = 422

        @staticmethod
        def json():
            return {"message": "recipient denied"}

    monkeypatch.setattr(
        email_delivery.requests,
        "post",
        lambda *args, **kwargs: Response(),
    )
    with pytest.raises(email_delivery.EmailDeliveryError, match="recipient denied"):
        email_delivery.send_feedback_reply(
            public_id="LT-20260906-ABCDEF12",
            to_email="user@example.com",
            reply="返信です。",
        )
