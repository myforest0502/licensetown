import os
from types import SimpleNamespace

os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ.setdefault("CHANNEL_ACCESS_TOKEN", "test-token")
os.environ.setdefault("CHANNEL_SECRET", "test-secret")

from app import app
from goukaku_ui import create_dashboard_token
import stripe_billing_ui as billing_ui


def test_sandbox_test_page_is_hidden_by_default(monkeypatch):
    monkeypatch.delenv("ENABLE_STRIPE_SANDBOX_CHECKOUT", raising=False)
    token = create_dashboard_token("learner-1")
    response = app.test_client().get(
        "/stripe/sandbox/test",
        query_string={"token": token},
    )
    assert response.status_code == 404


def test_sandbox_test_page_requires_signed_learner_token(monkeypatch):
    monkeypatch.setenv("ENABLE_STRIPE_SANDBOX_CHECKOUT", "1")
    response = app.test_client().get("/stripe/sandbox/test")
    assert response.status_code == 403


def test_sandbox_test_page_renders_post_forms(monkeypatch):
    monkeypatch.setenv("ENABLE_STRIPE_SANDBOX_CHECKOUT", "1")
    token = create_dashboard_token("learner-1")
    response = app.test_client().get(
        "/stripe/sandbox/test",
        query_string={"token": token},
    )

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Stripe サンドボックス確認" in html
    assert 'action="/stripe/sandbox/checkout"' in html
    assert 'action="/stripe/sandbox/portal"' in html
    assert f'value="{token}"' in html
    assert "実際の請求は発生しません" in html


def test_sandbox_checkout_route_is_hidden_by_default(monkeypatch):
    monkeypatch.delenv("ENABLE_STRIPE_SANDBOX_CHECKOUT", raising=False)
    token = create_dashboard_token("learner-1")
    response = app.test_client().post(
        "/stripe/sandbox/checkout",
        data={"token": token},
    )
    assert response.status_code == 404


def test_sandbox_checkout_requires_signed_learner_token(monkeypatch):
    monkeypatch.setenv("ENABLE_STRIPE_SANDBOX_CHECKOUT", "1")
    response = app.test_client().post("/stripe/sandbox/checkout")
    assert response.status_code == 403


def test_checkout_redirects_to_stripe_without_leaking_dashboard_token(monkeypatch):
    monkeypatch.setenv("ENABLE_STRIPE_SANDBOX_CHECKOUT", "1")
    token = create_dashboard_token("learner-1")
    captured = {}

    def fake_create(user_id, *, success_url, cancel_url):
        captured.update(
            user_id=user_id,
            success_url=success_url,
            cancel_url=cancel_url,
        )
        return SimpleNamespace(url="https://checkout.stripe.test/session")

    monkeypatch.setattr(billing_ui, "create_subscription_checkout_session", fake_create)
    response = app.test_client().post(
        "/stripe/sandbox/checkout",
        data={"token": token},
    )

    assert response.status_code == 303
    assert response.headers["Location"] == "https://checkout.stripe.test/session"
    assert captured["user_id"] == "learner-1"
    assert token not in captured["success_url"]
    assert token not in captured["cancel_url"]
    assert "checkout=success" in captured["success_url"]
    assert "checkout=cancel" in captured["cancel_url"]


def test_sandbox_portal_requires_signed_learner_token(monkeypatch):
    monkeypatch.setenv("ENABLE_STRIPE_SANDBOX_CHECKOUT", "1")
    response = app.test_client().post("/stripe/sandbox/portal")
    assert response.status_code == 403


def test_portal_redirects_to_stripe(monkeypatch):
    monkeypatch.setenv("ENABLE_STRIPE_SANDBOX_CHECKOUT", "1")
    token = create_dashboard_token("learner-1")
    captured = {}

    def fake_portal(user_id, *, return_url):
        captured.update(user_id=user_id, return_url=return_url)
        return {"url": "https://billing.stripe.test/portal"}

    monkeypatch.setattr(billing_ui, "create_customer_portal_session", fake_portal)
    response = app.test_client().post(
        "/stripe/sandbox/portal",
        data={"token": token},
    )

    assert response.status_code == 303
    assert response.headers["Location"] == "https://billing.stripe.test/portal"
    assert captured["user_id"] == "learner-1"
    assert token not in captured["return_url"]
