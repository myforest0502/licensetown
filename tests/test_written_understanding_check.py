import os
from types import SimpleNamespace

os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ.setdefault("CHANNEL_ACCESS_TOKEN", "test-token")
os.environ.setdefault("CHANNEL_SECRET", "test-secret")

import app
from database import get_question_attempts, get_written_check_history
from written_understanding_check import (
    build_written_prompt,
    evaluation_fallback,
    parse_structured_evaluation,
    select_written_check_candidate,
    should_offer_written_check,
    unknown_evaluation,
)


def test_offer_requires_correct_and_wrong_evidence():
    assert should_offer_written_check([{"is_correct": True}, {"is_correct": False}])
    assert not should_offer_written_check([{"is_correct": True}])
    assert not should_offer_written_check([{"is_correct": False}])


def test_candidate_uses_canonical_node_and_avoids_same_session_duplicate():
    session = [{"question_id": "Q1", "knowledge_node_id": "KN0807", "is_correct": True}]
    history = [
        {"question_id": "Q1", "knowledge_node_id": "KN0807", "is_correct": True},
        {"question_id": "Q2", "knowledge_node_id": "KN0597", "is_correct": False},
    ]
    candidate = select_written_check_candidate(session, history)
    assert candidate == {"canonical_node_id": "KN0597", "source_question_id": "Q1"}
    assert select_written_check_candidate(
        session, history, used_canonical_node_ids=["KN0597"]
    ) is None


def test_fixed_prompt_is_short_and_does_not_use_ai():
    prompt = build_written_prompt("遠心性収縮")
    assert "遠心性収縮" in prompt
    assert "1〜2文" in prompt


def test_structured_evaluation_accepts_three_levels():
    for level in ("PASS", "PARTIAL", "FAIL"):
        result = parse_structured_evaluation(
            f'{{"result":"{level}","reason":"理由","feedback":"返答"}}'
        )
        assert result["result"] == level


def test_unknown_and_ai_failure_fallback_are_short_and_structured():
    assert unknown_evaluation()["result"] == "UNKNOWN"
    assert evaluation_fallback()["result"] == "PARTIAL"


def _waiting_session():
    return {
        "session_id": "written-test-session",
        "mode": "study",
        "status": "waiting_for_written_answer",
        "pending_written_check": {
            "canonical_node_id": "KN0001",
            "source_question_id": "Q1",
            "written_prompt": "説明してくれ。",
            "knowledge_node": "確認対象",
            "formal_answer": "A",
            "formal_explanation": "正式解説",
        },
    }


def test_free_text_is_consumed_as_written_answer_not_normal_parser(monkeypatch):
    user_id = "written-free-text"
    app.study_sessions[user_id] = _waiting_session()
    saved = []
    monkeypatch.setattr(app, "evaluate_written_answer", lambda *_: {
        "result": "PASS", "reason": "ok", "feedback": "よし"
    })
    monkeypatch.setattr(app, "save_written_check_result", lambda *args: saved.append(args))
    monkeypatch.setattr(app, "reply_written_check_result", lambda *_: None)
    assert app.process_study_flow_command("token", user_id, "A1 B2 C3 D1 E2")
    assert saved[0][3] == "A1 B2 C3 D1 E2"
    assert app.study_sessions[user_id]["status"] == "quiz_completed"
    app.study_sessions.pop(user_id, None)


def test_written_zero_skips_ai_and_persists_unknown(monkeypatch):
    user_id = "written-zero"
    app.study_sessions[user_id] = _waiting_session()
    saved = []
    monkeypatch.setattr(app, "evaluate_written_answer", lambda *_: (_ for _ in ()).throw(AssertionError()))
    monkeypatch.setattr(app, "save_written_check_result", lambda *args: saved.append(args))
    monkeypatch.setattr(app, "reply_written_check_result", lambda *_: None)
    assert app.process_study_flow_command("token", user_id, "0")
    assert saved[0][4]["result"] == "UNKNOWN"
    app.study_sessions.pop(user_id, None)


def test_ai_failure_uses_fallback_and_still_saves(monkeypatch):
    user_id = "written-fallback"
    app.study_sessions[user_id] = _waiting_session()
    saved = []
    monkeypatch.setattr(app, "evaluate_written_answer", lambda *_: (_ for _ in ()).throw(RuntimeError("down")))
    monkeypatch.setattr(app, "save_written_check_result", lambda *args: saved.append(args))
    monkeypatch.setattr(app, "reply_written_check_result", lambda *_: None)
    assert app.process_study_flow_command("token", user_id, "説明")
    assert saved and saved[0][4]["result"] == "PARTIAL"
    app.study_sessions.pop(user_id, None)


def test_written_result_persistence_creates_no_question_attempt_or_node_update():
    user_id = "written-persistence"
    session = _waiting_session()
    app.save_written_check_result(
        user_id,
        session,
        session["pending_written_check"],
        "自分の説明",
        {"result": "PASS", "reason": "中心概念あり", "feedback": "よし"},
    )
    assert get_question_attempts(user_id) == []
    saved = get_written_check_history(user_id)
    assert saved[0]["canonical_node_id"] == "KN0001"
    assert saved[0]["source_question_id"] == "Q1"
    assert saved[0]["written_answer_status"] == "answered"
    assert saved[0]["evaluation"] == "PASS"


def test_completion_offers_written_check_only_when_candidate_exists(monkeypatch):
    user_id = "written-offer"
    session = {
        "mode": "study", "status": "waiting_for_explanations",
        "session_kind": "adaptive_daily", "question_count": 30,
    }
    app.study_sessions[user_id] = session
    monkeypatch.setattr(app, "advance_quiz_explanations", lambda current: current.update(status="quiz_completed") or ["解説"])
    monkeypatch.setattr(app, "build_pending_written_check", lambda *_: {"canonical_node_id": "KN1", "written_prompt": "説明"})
    offered = []
    monkeypatch.setattr(app, "reply_written_check_offer", lambda *args: offered.append(args))
    assert app.process_study_flow_command("token", user_id, "解答解説を見る")
    assert session["status"] == "waiting_for_written_answer"
    assert offered
    app.study_sessions.pop(user_id, None)


def test_completion_remains_legacy_when_no_candidate(monkeypatch):
    user_id = "written-no-offer"
    session = {
        "mode": "study", "status": "waiting_for_explanations",
        "session_kind": "adaptive_daily", "question_count": 30,
    }
    app.study_sessions[user_id] = session
    monkeypatch.setattr(app, "advance_quiz_explanations", lambda current: current.update(status="quiz_completed") or ["解説"])
    monkeypatch.setattr(app, "build_pending_written_check", lambda *_: None)
    completed = []
    monkeypatch.setattr(app, "reply_explanation_choice", lambda *args, **kwargs: completed.append(kwargs))
    assert app.process_study_flow_command("token", user_id, "解答解説を見る")
    assert completed[0]["completed"] is True
    app.study_sessions.pop(user_id, None)


def test_gensan_pause_clears_written_waiting_state(monkeypatch):
    user_id = "written-pause"
    app.study_sessions[user_id] = _waiting_session()
    monkeypatch.setattr(app, "return_home", lambda *_args, **_kwargs: None)
    assert app.process_study_flow_command("token", user_id, "源さんに預ける")
    assert user_id not in app.study_sessions


def test_written_check_not_offered_for_nekketsu_or_non_30_session():
    assert app.build_pending_written_check("u", {
        "session_kind": "random", "question_count": 30
    }) is None
    assert app.build_pending_written_check("u", {
        "session_kind": "adaptive_daily", "question_count": 10
    }) is None
