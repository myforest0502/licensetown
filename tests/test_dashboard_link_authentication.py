import os
from urllib.parse import parse_qs, urlparse

os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ.setdefault("CHANNEL_ACCESS_TOKEN", "test-token")
os.environ.setdefault("CHANNEL_SECRET", "test-secret")

import app as app_module
from app import app


def _assert_authenticated_dashboard_url(url, user_id):
    parsed = urlparse(url)
    assert parsed.path == "/goukaku-no-michi"
    token = parse_qs(parsed.query)["token"][0]
    assert app_module.dashboard_user_id(token) == user_id
    return token


def test_home_message_uses_authenticated_direct_dashboard_url_with_liff(monkeypatch):
    monkeypatch.setenv("LIFF_ID", "1234567890-test")
    monkeypatch.setenv("PUBLIC_BASE_URL", "https://example.test")

    message = app_module.create_home_message("home-dashboard-user")
    dashboard_url = message.quick_reply.items[0].action.uri
    token = _assert_authenticated_dashboard_url(dashboard_url, "home-dashboard-user")

    assert not dashboard_url.startswith("https://liff.line.me/")
    assert app.test_client().get(f"/goukaku-no-michi?token={token}").status_code == 200


def test_dashboard_text_reply_keeps_authenticated_token(monkeypatch):
    monkeypatch.setenv("LIFF_ID", "1234567890-test")
    monkeypatch.setenv("PUBLIC_BASE_URL", "https://example.test")
    replies = []
    monkeypatch.setattr(app_module, "reply_to_line", lambda token, text: replies.append((token, text)))

    app_module.reply_dashboard_link("reply-token", "reply-dashboard-user")

    dashboard_url = replies[0][1].splitlines()[-1]
    _assert_authenticated_dashboard_url(dashboard_url, "reply-dashboard-user")


def test_dashboard_route_remains_fail_closed():
    client = app.test_client()
    assert client.get("/goukaku-no-michi").status_code == 403
    assert client.get("/goukaku-no-michi?token=invalid").status_code == 403


def test_liff_state_recovers_signed_dashboard_token():
    token = app_module.create_dashboard_token("liff-state-user")

    response = app.test_client().get(
        "/goukaku-no-michi",
        query_string={"liff.state": f"?token={token}"},
    )

    assert response.status_code == 200
    assert f'data-dashboard-token="{token}"' in response.get_data(as_text=True)


def test_liff_state_remains_fail_closed_for_invalid_missing_and_malformed_token():
    client = app.test_client()
    states = (
        "?token=invalid",
        "?foo=bar",
        "not-a-query",
        "?token",
        "?token=",
        "?token=one&token=two",
    )

    for state in states:
        assert client.get(
            "/goukaku-no-michi",
            query_string={"liff.state": state},
        ).status_code == 403


def test_top_level_token_has_priority_over_invalid_liff_state():
    token = app_module.create_dashboard_token("top-level-user")

    response = app.test_client().get(
        "/goukaku-no-michi",
        query_string={"token": token, "liff.state": "?token=invalid&broken"},
    )

    assert response.status_code == 200
    assert f'data-dashboard-token="{token}"' in response.get_data(as_text=True)


def test_invalid_top_level_token_is_not_replaced_by_valid_liff_state():
    liff_token = app_module.create_dashboard_token("liff-state-user")

    response = app.test_client().get(
        "/goukaku-no-michi",
        query_string={"token": "invalid", "liff.state": f"?token={liff_token}"},
    )

    assert response.status_code == 403
