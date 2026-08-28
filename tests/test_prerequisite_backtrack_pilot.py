from datetime import datetime, timedelta, timezone
import logging
import os

os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ.setdefault("CHANNEL_ACCESS_TOKEN", "test-token")
os.environ.setdefault("CHANNEL_SECRET", "test-secret")

import app
from knowledge_node_relations import get_node_relations, get_reviewed_node_relations
from prerequisite_backtrack_pilot import (
    build_pending_backtrack_candidate,
    inject_pending_backtrack_candidate,
    is_prerequisite_backtrack_pilot_enabled,
    parse_prerequisite_backtrack_pilot_user_ids,
)


NOW = datetime(2026, 8, 29, tzinfo=timezone.utc)
MIP = next(item for item in get_reviewed_node_relations() if item["relation_id"] == "KNR0003")


def attempt(question, node, correct, confidence, minute, event="event", user="user-a"):
    return {
        "event_key": event,
        "user_id": user,
        "question_id": question,
        "knowledge_node_id": node,
        "is_correct": correct,
        "confidence": confidence,
        "answered_at": NOW + timedelta(minutes=minute),
        "attempt_position": 1,
    }


def questions(*ids):
    return [{"id": question_id} for question_id in ids]


def test_mip_wrong_queues_q260_for_next_set():
    source = attempt("Q260", MIP["source_node_id"], True, 2, 1)
    target = attempt("Q386", MIP["target_node_id"], False, 2, 2, "session:1")
    candidate = build_pending_backtrack_candidate([target], [source, target], [MIP])
    assert candidate["question_id"] == "Q260"
    assert candidate["source_status"] == "SOURCE_UNSTABLE"
    updated, injected = inject_pending_backtrack_candidate(
        questions("Q1", "Q2", "Q3", "Q4", "Q5", "Q6", "Q7", "Q8", "Q9", "Q10"),
        candidate,
        5,
        5,
        lambda question_id: {"id": question_id},
    )
    assert injected
    assert [item["id"] for item in updated[5:10]].count("Q260") == 1
    assert updated[5]["id"] == "Q260"


def test_correct_target_never_queues_backtrack():
    target = attempt("Q386", MIP["target_node_id"], True, 1, 2)
    assert build_pending_backtrack_candidate([target], [target], [MIP]) is None


def test_confident_correct_source_keeps_target_self_repair():
    source = attempt("Q260", MIP["source_node_id"], True, 1, 1)
    target = attempt("Q386", MIP["target_node_id"], False, 2, 2)
    assert build_pending_backtrack_candidate([target], [source, target], [MIP]) is None


def test_unseen_and_conflict_source_queue_candidate():
    target = attempt("Q386", MIP["target_node_id"], False, 2, 2)
    unseen = build_pending_backtrack_candidate([target], [target], [MIP])
    wrong_source = attempt("Q260", MIP["source_node_id"], False, 1, 1)
    conflict = build_pending_backtrack_candidate(
        [target], [wrong_source, target], [MIP]
    )
    assert unseen["question_id"] == "Q260"
    assert unseen["source_status"] == "SOURCE_UNSEEN"
    assert conflict["question_id"] == "Q260"
    assert conflict["source_status"] == "SOURCE_CONFLICT"


def test_medium_transfer_is_ignored():
    transfer = next(item for item in get_node_relations() if item["relation_type"] == "TRANSFER")
    target = attempt("Q246", transfer["target_node_id"], False, 2, 2)
    assert build_pending_backtrack_candidate([target], [target], [transfer]) is None


def test_excluded_source_and_target_self_are_not_candidates():
    target = attempt("Q386", MIP["target_node_id"], False, 2, 2)
    assert build_pending_backtrack_candidate(
        [target], [target], [MIP], excluded_question_ids={"Q260"}
    ) is None


def test_injection_preserves_length_uniqueness_and_maximum_one_question():
    original = questions("Q1", "Q2", "Q3", "Q4", "Q5", "Q6", "Q7", "Q8", "Q260", "Q10")
    candidate = {"question_id": "Q260", "depth": 1}
    updated, injected = inject_pending_backtrack_candidate(
        original, candidate, 5, 5, lambda question_id: {"id": question_id}
    )
    ids = [item["id"] for item in updated]
    assert injected
    assert len(ids) == len(original)
    assert len(ids) == len(set(ids))
    assert ids[5] == "Q260"
    assert ids[5:10].count("Q260") == 1


def test_previous_question_and_invalid_depth_prevent_injection():
    original = questions("Q260", "Q2", "Q3", "Q4", "Q5", "Q6", "Q7", "Q8", "Q9", "Q10")
    unchanged, injected = inject_pending_backtrack_candidate(
        original, {"question_id": "Q260", "depth": 1}, 5, 5,
        lambda question_id: {"id": question_id},
    )
    recursive, recursive_injected = inject_pending_backtrack_candidate(
        original, {"question_id": "Q11", "depth": 2}, 5, 5,
        lambda question_id: {"id": question_id},
    )
    assert not injected
    assert not recursive_injected
    assert unchanged == original
    assert recursive == original


def test_allowlist_parser_trims_ignores_empty_and_deduplicates():
    assert parse_prerequisite_backtrack_pilot_user_ids(
        " abc, def,abc, , "
    ) == {"abc", "def"}
    assert parse_prerequisite_backtrack_pilot_user_ids(None) == set()


def test_pilot_gate_fails_closed():
    assert not is_prerequisite_backtrack_pilot_enabled(False, "abc", {"abc"})
    assert not is_prerequisite_backtrack_pilot_enabled(True, "abc", set())
    assert not is_prerequisite_backtrack_pilot_enabled(True, "other", {"abc"})
    assert is_prerequisite_backtrack_pilot_enabled(True, "abc", {"abc", "def"})


def session_questions():
    ids = ["Q386", "Q2", "Q3", "Q4", "Q5"] + [
        f"Q{number}" for number in range(6, 31)
    ]
    return [{"id": question_id} for question_id in ids]


def make_session():
    all_questions = session_questions()
    return {
        "session_id": "pilot-session",
        "status": "waiting_for_continue",
        "current_set": 1,
        "question_count": 30,
        "questions_per_set": 5,
        "total_sets": 6,
        "questions": all_questions[:5],
        "all_questions": all_questions,
        "all_answers": {},
        "mode": "study",
        "session_kind": "adaptive_daily",
    }


def test_feature_flag_false_skips_history_and_preserves_existing_next_set(monkeypatch):
    session = make_session()
    original_ids = [item["id"] for item in session["all_questions"]]
    session["pending_prerequisite_backtrack"] = {
        "question_id": "Q260", "depth": 1
    }
    app.study_sessions["flag-off-user"] = session
    monkeypatch.setattr(app, "ENABLE_PREREQUISITE_BACKTRACK", False)
    monkeypatch.setattr(
        app, "PREREQUISITE_BACKTRACK_PILOT_USER_IDS", {"flag-off-user"}
    )
    monkeypatch.setattr(
        app,
        "get_question_attempts",
        lambda _user_id: (_ for _ in ()).throw(AssertionError("history fetched")),
    )
    monkeypatch.setattr(app, "format_quiz_messages", lambda *args, **kwargs: ["ok"])
    try:
        assert app.queue_prerequisite_backtrack_for_next_set("flag-off-user", session) is None
        app.start_next_quiz("flag-off-user")
        assert [item["id"] for item in session["all_questions"]] == original_ids
        assert [item["id"] for item in session["questions"]] == original_ids[5:10]
        assert "pending_prerequisite_backtrack" in session
    finally:
        app.study_sessions.pop("flag-off-user", None)


def test_feature_flag_true_queues_one_mip_candidate_without_recursion(monkeypatch, caplog):
    caplog.set_level(logging.INFO)
    session = make_session()
    source = attempt("Q260", MIP["source_node_id"], True, 2, 1, "old-event", "pilot-user")
    target = attempt(
        "Q386", MIP["target_node_id"], False, 2, 2, "pilot-session:1", "pilot-user"
    )
    app.study_sessions["pilot-user"] = session
    monkeypatch.setattr(app, "ENABLE_PREREQUISITE_BACKTRACK", True)
    monkeypatch.setattr(app, "PREREQUISITE_BACKTRACK_PILOT_USER_IDS", {"pilot-user"})
    monkeypatch.setattr(app, "get_question_attempts", lambda _user_id: [source, target])
    monkeypatch.setattr(app, "get_reviewed_node_relations", lambda: [MIP])
    monkeypatch.setattr(app, "get_quiz_question", lambda question_id: {"id": question_id})
    monkeypatch.setattr(app, "format_quiz_messages", lambda *args, **kwargs: ["ok"])
    try:
        candidate = app.queue_prerequisite_backtrack_for_next_set("pilot-user", session)
        assert candidate["question_id"] == "Q260"
        app.start_next_quiz("pilot-user")
        assert session["current_set"] == 2
        assert session["questions"][0]["id"] == "Q260"
        assert sum(item["id"] == "Q260" for item in session["questions"]) == 1
        assert session["prerequisite_backtrack_set"] == 2
        assert app.queue_prerequisite_backtrack_for_next_set("pilot-user", session) is None
        assert "pending_prerequisite_backtrack" not in session
        assert "event=prerequisite_backtrack_selected" in caplog.text
        assert "relation_id=KNR0003" in caplog.text
        assert "source_question_id=Q260" in caplog.text
        assert "target_question_id=Q386" in caplog.text
        assert "diagnosis=SOURCE_UNSTABLE" in caplog.text
        assert "reason=uncertain_or_guessed_correct_source" in caplog.text
        assert "pilot-user" not in caplog.text
    finally:
        app.study_sessions.pop("pilot-user", None)


def test_non_allowlisted_and_empty_allowlist_skip_history(monkeypatch):
    session = make_session()
    app.study_sessions["outside-user"] = session
    monkeypatch.setattr(app, "ENABLE_PREREQUISITE_BACKTRACK", True)
    monkeypatch.setattr(
        app,
        "get_question_attempts",
        lambda _user_id: (_ for _ in ()).throw(AssertionError("history fetched")),
    )
    try:
        monkeypatch.setattr(app, "PREREQUISITE_BACKTRACK_PILOT_USER_IDS", set())
        assert app.queue_prerequisite_backtrack_for_next_set("outside-user", session) is None
        monkeypatch.setattr(app, "PREREQUISITE_BACKTRACK_PILOT_USER_IDS", {"pilot-user"})
        assert app.queue_prerequisite_backtrack_for_next_set("outside-user", session) is None
        assert "pending_prerequisite_backtrack" not in session
    finally:
        app.study_sessions.pop("outside-user", None)
