import os

os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ.setdefault("CHANNEL_ACCESS_TOKEN", "test-token")
os.environ.setdefault("CHANNEL_SECRET", "test-secret")

import stripe

from app import app
import stripe_webhook_ui as webhook_module


def test_stripe_webhook_route_is_registered(monkeypatch):
    monkeypatch.setattr(
        webhook_module,
        "process_stripe_webhook",
        lambda payload, signature: {
            "handled": True,
            "duplicate": False,
            "stale": False,
        },
    )

    response = app.test_client().post(
        "/stripe/webhook",
        data=b"{}",
        headers={"Stripe-Signature": "t=1,v1=test"},
    )

    assert response.status_code == 200
    assert response.get_json() == {
        "ok": True,
        "handled": True,
        "duplicate": False,
        "stale": False,
    }


def test_invalid_stripe_signature_is_rejected(monkeypatch):
    def reject(payload, signature):
        raise stripe.SignatureVerificationError("bad signature", signature)

    monkeypatch.setattr(webhook_module, "process_stripe_webhook", reject)

    response = app.test_client().post(
        "/stripe/webhook",
        data=b"{}",
        headers={"Stripe-Signature": "bad"},
    )

    assert response.status_code == 400
    assert response.get_json() == {"ok": False}


def test_unconfigured_webhook_fails_closed(monkeypatch):
    def unconfigured(payload, signature):
        raise RuntimeError("missing secret")

    monkeypatch.setattr(webhook_module, "process_stripe_webhook", unconfigured)

    response = app.test_client().post(
        "/stripe/webhook",
        data=b"{}",
        headers={"Stripe-Signature": "t=1,v1=test"},
    )

    assert response.status_code == 503
    assert response.get_json() == {"ok": False}
