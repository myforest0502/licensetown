import logging
import os
from types import SimpleNamespace

import pytest

os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ.setdefault("CHANNEL_ACCESS_TOKEN", "test-token")
os.environ.setdefault("CHANNEL_SECRET", "test-secret")

import app as bot_app
import goukaku_ui
import learner_path_performance as performance


def _operations(caplog):
    return [record.getMessage() for record in caplog.records if "lt_learner_path_perf" in record.getMessage()]


def test_performance_flag_off_is_noop(monkeypatch, caplog):
    monkeypatch.delenv("LT_LEARNER_PATH_PERF_LOG", raising=False)
    with caplog.at_level(logging.INFO, logger=performance.__name__):
        with performance.measure("test.operation"):
            pass
    assert _operations(caplog) == []


def test_performance_log_contains_only_operation_duration_and_outcome(monkeypatch, caplog):
    monkeypatch.setenv("LT_LEARNER_PATH_PERF_LOG", "true")
    secret = "private-user-token-and-answer"
    with caplog.at_level(logging.INFO, logger=performance.__name__):
        with performance.measure("test.operation"):
            _ = secret
    messages = _operations(caplog)
    assert len(messages) == 1
    assert "op=test.operation" in messages[0]
    assert "duration_ms=" in messages[0]
    assert "outcome=ok" in messages[0]
    assert secret not in messages[0]


def test_sync_and_async_study_start_keep_existing_send_semantics(monkeypatch, caplog):
    monkeypatch.setenv("LT_LEARNER_PATH_PERF_LOG", "1")
    calls = []

    def start(user_id, **_kwargs):
        calls.append(("start", user_id))
        bot_app.study_sessions[user_id] = {"questions": []}
        return ["first-five"]

    monkeypatch.setattr(bot_app, "start_quiz", start)
    monkeypatch.setattr(bot_app, "reply_current_quiz", lambda token, session, **_kwargs: calls.append(("reply", token, session)))
    monkeypatch.setattr(bot_app, "show_loading_animation", lambda user_id: calls.append(("loading", user_id)))
    monkeypatch.setattr(bot_app, "push_quiz_to_line", lambda user_id, message: calls.append(("push", user_id, message)))

    with caplog.at_level(logging.INFO, logger=performance.__name__):
        assert bot_app.start_and_reply_quiz("reply-token", "sync-user") is True
        bot_app.prepare_and_send_quiz("async-user")

    assert calls[0][:2] == ("start", "sync-user")
    assert calls[1][0:2] == ("reply", "reply-token")
    assert ("loading", "async-user") in calls
    assert ("push", "async-user", "first-five") in calls
    messages = "\n".join(_operations(caplog))
    for operation in (
        "study_start.selector_build", "study_start.line_send", "study_start.total",
        "study_start_async.selector_build", "study_start_async.line_send", "study_start_async.total",
    ):
        assert f"op={operation}" in messages


def test_five_answer_path_keeps_parse_persist_and_reply(monkeypatch, caplog):
    monkeypatch.setenv("LT_LEARNER_PATH_PERF_LOG", "1")
    user_id = "answer-user"
    session = {
        "mode": "study", "status": "waiting_for_answers", "current_set": 1,
        "questions_per_set": 5, "expected_numbers": [1, 2, 3, 4, 5],
        "all_answers": {}, "total_sets": 2,
    }
    bot_app.study_sessions[user_id] = session
    persisted = []
    replies = []
    parsed = {number: {"answer": "A", "confidence": "1"} for number in range(1, 6)}
    monkeypatch.setattr(bot_app, "parse_quiz_answers", lambda *_args, **_kwargs: parsed)
    monkeypatch.setattr(bot_app, "record_confirmed_learning_batch", lambda uid, saved: persisted.append((uid, saved)))
    monkeypatch.setattr(bot_app, "queue_prerequisite_backtrack_for_next_set", lambda *_args: None)
    monkeypatch.setattr(bot_app, "reply_study_set_result", lambda token, saved: replies.append((token, saved["status"])))

    with caplog.at_level(logging.INFO, logger=performance.__name__):
        assert bot_app.process_study_answer_input("reply-token", user_id, "answers") is True

    assert persisted == [(user_id, session)]
    assert replies == [("reply-token", "waiting_for_continue")]
    assert len(session["all_answers"]) == 5
    messages = "\n".join(_operations(caplog))
    for operation in ("study_answer.parse", "study_answer.persist", "study_answer.reply", "study_answer.total"):
        assert f"op={operation}" in messages


def test_non_study_dispatch_probe_does_not_emit_study_answer_total(monkeypatch, caplog):
    monkeypatch.setenv("LT_LEARNER_PATH_PERF_LOG", "1")
    user_id = "not-an-answer-user"
    bot_app.study_sessions.pop(user_id, None)

    with caplog.at_level(logging.INFO, logger=performance.__name__):
        assert bot_app.process_study_answer_input("reply-token", user_id, "hello") is False

    messages = "\n".join(_operations(caplog))
    assert "op=study_answer.total" not in messages


def test_consultation_times_one_ai_call_and_one_line_reply(monkeypatch, caplog):
    monkeypatch.setenv("LT_LEARNER_PATH_PERF_LOG", "1")
    user_id = "consult-user"
    bot_app.user_names[user_id] = "learner"
    bot_app.user_modes[user_id] = "chat"
    bot_app.user_states[user_id] = "consultation_input"
    calls = []
    monkeypatch.setattr(bot_app, "user_profile_exists", lambda _user_id: True)
    monkeypatch.setattr(bot_app, "process_study_flow_command", lambda *_args: False)
    monkeypatch.setattr(bot_app, "process_nekketsu_flow_command", lambda *_args: False)
    monkeypatch.setattr(bot_app, "process_study_answer_input", lambda *_args: False)
    monkeypatch.setattr(bot_app, "create_text_response", lambda text, mode: calls.append(("ai", text, mode)) or "response")
    monkeypatch.setattr(bot_app, "record_activity_event", lambda *_args: None)
    monkeypatch.setattr(bot_app, "reply_consultation_response", lambda token, text: calls.append(("reply", token, text)))
    event = SimpleNamespace(
        source=SimpleNamespace(user_id=user_id),
        message=SimpleNamespace(text="private consultation"),
        reply_token="private reply token",
    )

    with caplog.at_level(logging.INFO, logger=performance.__name__):
        bot_app.handle_text_message(event)

    assert [call[0] for call in calls] == ["ai", "reply"]
    messages = "\n".join(_operations(caplog))
    for operation in ("consult.openai", "consult.line_send", "consult.total"):
        assert f"op={operation}" in messages
    assert "private consultation" not in messages
    assert "private reply token" not in messages


def test_consultation_total_marks_propagating_error(monkeypatch, caplog):
    monkeypatch.setenv("LT_LEARNER_PATH_PERF_LOG", "1")
    user_id = "consult-error-user"
    bot_app.user_names[user_id] = "learner"
    bot_app.user_modes[user_id] = "chat"
    bot_app.user_states[user_id] = "consultation_input"
    monkeypatch.setattr(bot_app, "user_profile_exists", lambda _user_id: True)
    monkeypatch.setattr(bot_app, "process_study_flow_command", lambda *_args: False)
    monkeypatch.setattr(bot_app, "process_nekketsu_flow_command", lambda *_args: False)
    monkeypatch.setattr(bot_app, "process_study_answer_input", lambda *_args: False)
    monkeypatch.setattr(bot_app, "create_text_response", lambda *_args: "response")

    def fail_activity(*_args):
        raise RuntimeError("activity write failed")

    monkeypatch.setattr(bot_app, "record_activity_event", fail_activity)
    event = SimpleNamespace(
        source=SimpleNamespace(user_id=user_id),
        message=SimpleNamespace(text="private consultation"),
        reply_token="private reply token",
    )

    with caplog.at_level(logging.INFO, logger=performance.__name__):
        with pytest.raises(RuntimeError, match="activity write failed"):
            bot_app.handle_text_message(event)

    messages = _operations(caplog)
    consult_total = [message for message in messages if "op=consult.total" in message]
    assert len(consult_total) == 1
    assert "outcome=error" in consult_total[0]


def test_dashboard_times_existing_build_activity_and_render(monkeypatch, caplog):
    monkeypatch.setenv("LT_LEARNER_PATH_PERF_LOG", "1")
    token = goukaku_ui.create_dashboard_token("dashboard-user")
    recorded = []
    monkeypatch.setattr(goukaku_ui, "record_activity_event", lambda *args: recorded.append(args))

    with caplog.at_level(logging.INFO, logger=performance.__name__):
        response = bot_app.app.test_client().get(f"/goukaku-no-michi?token={token}")

    assert response.status_code == 200
    assert recorded and recorded[0][1] == "recommendation_plan"
    messages = "\n".join(_operations(caplog))
    for operation in (
        "dashboard.build", "dashboard.activity_record",
        "dashboard.template_render", "dashboard.route_total",
    ):
        assert f"op={operation}" in messages
