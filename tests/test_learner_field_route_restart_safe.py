import os
from types import SimpleNamespace

os.environ.setdefault("OPENAI_API_KEY", "test-openai-key")
os.environ.setdefault("CHANNEL_ACCESS_TOKEN", "test-line-token")
os.environ.setdefault("CHANNEL_SECRET", "test-line-secret")
os.environ.setdefault("LINE_CHANNEL_ACCESS_TOKEN", "test-line-token")
os.environ.setdefault("LINE_CHANNEL_SECRET", "test-line-secret")

import pytest

import app


def _event(text, user_id="route-user"):
    return SimpleNamespace(
        message=SimpleNamespace(text=text),
        source=SimpleNamespace(user_id=user_id),
        reply_token="reply-token",
    )


def _clear(user_id):
    app.user_states.pop(user_id, None)
    app.user_modes.pop(user_id, None)
    app.quiz_category_selections.pop(user_id, None)
    app.study_sessions.pop(user_id, None)


def test_self_describing_group_commands_round_trip_all_groups():
    for mode in ("study", "nekketsu"):
        for group in app.get_category_group_names():
            command = app.build_category_group_command(mode, group)
            parsed = app.parse_category_route_command(command)
            assert parsed == {
                "kind": "group",
                "mode": mode,
                "group_name": group,
            }


def test_self_describing_small_commands_round_trip_all_fields():
    for mode in ("study", "nekketsu"):
        for group in app.get_category_group_names():
            for field in app.get_category_names_for_group(group):
                command = app.build_category_small_command(mode, group, field)
                parsed = app.parse_category_route_command(command)
                assert parsed["kind"] == "small"
                assert parsed["mode"] == mode
                assert parsed["group_name"] == group
                assert parsed["field_name"] == field
                assert parsed["category_small"] == app.resolve_category_small(field, group)


@pytest.mark.parametrize("mode,label", [("study", "学習"), ("nekketsu", "熱血")])
def test_group_payload_recovers_after_transient_state_loss(monkeypatch, mode, label):
    user_id = f"group-{mode}"
    _clear(user_id)
    captured = {}

    monkeypatch.setattr(
        app,
        "reply_quiz_category_choice",
        lambda reply_token, group_name, mode="study": captured.update(
            reply_token=reply_token, group_name=group_name, mode=mode
        ),
    )

    group = app.get_category_group_names()[0]
    app.handle_text_message(_event(f"{label}：分野：{group}", user_id))

    assert app.user_modes[user_id] == mode
    assert app.user_states[user_id] == "waiting_quiz_category_small"
    assert app.quiz_category_selections[user_id] == {
        "mode": mode,
        "group_name": group,
    }
    assert captured == {
        "reply_token": "reply-token",
        "group_name": group,
        "mode": mode,
    }


@pytest.mark.parametrize("mode,label", [("study", "学習"), ("nekketsu", "熱血")])
def test_small_payload_starts_selected_field_after_transient_state_loss(monkeypatch, mode, label):
    user_id = f"small-{mode}"
    _clear(user_id)
    captured = {}

    monkeypatch.setattr(
        app,
        "start_and_reply_quiz",
        lambda reply_token, uid: captured.update(reply_token=reply_token, user_id=uid),
    )

    group = app.get_category_group_names()[0]
    field = app.get_category_names_for_group(group)[0]
    expected_category = app.resolve_category_small(field, group)

    app.handle_text_message(_event(f"{label}：分野：{group}：{field}", user_id))

    assert app.user_modes[user_id] == mode
    assert user_id not in app.user_states
    assert app.quiz_category_selections[user_id] == {
        "mode": mode,
        "group_name": group,
        "category_small": expected_category,
    }
    assert captured == {"reply_token": "reply-token", "user_id": user_id}


def test_invalid_self_describing_payload_does_not_parse():
    assert app.parse_category_route_command("学習：分野：存在しない分類") is None
    assert app.parse_category_route_command("熱血：分野：基礎：存在しない分野") is None
    assert app.parse_category_route_command("分野：基礎") is None
