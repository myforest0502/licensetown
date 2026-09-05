from types import SimpleNamespace

from prerequisite_attempt_cache import install_prerequisite_attempt_cache


def _legacy():
    user_id = "pilot-user"
    old_attempt = {
        "event_key": "old:1",
        "user_id": user_id,
        "question_id": "Q260",
        "knowledge_node_id": "source-node",
        "is_correct": True,
        "confidence": 2,
        "answered_at": "2026-09-05T00:00:00+00:00",
        "attempt_position": 1,
    }
    target_question = {"id": "Q386"}
    filler = [{"id": f"Q{number}"} for number in range(2, 31)]
    all_questions = [target_question, *filler]
    legacy = SimpleNamespace(
        ENABLE_PREREQUISITE_BACKTRACK=True,
        PREREQUISITE_BACKTRACK_PILOT_USER_IDS={user_id},
        study_sessions={},
        db_queue_calls=0,
    )

    legacy.is_prerequisite_backtrack_pilot_enabled = (
        lambda enabled, uid, allowlist: bool(enabled and uid in allowlist)
    )
    legacy.get_question_tag = lambda question_id: {
        "knowledge_node_id": "target-node" if question_id == "Q386" else "other-node"
    }
    legacy.is_answer_correct = lambda question, answer: answer == "A"
    legacy.get_reviewed_node_relations = lambda: ["relation"]

    def build_pending(current_attempts, attempts, relations, excluded_question_ids=()):
        assert current_attempts[0]["event_key"] == "session-1:1"
        assert old_attempt in attempts
        assert relations == ["relation"]
        return {"question_id": "Q260", "depth": 1}

    legacy.build_pending_backtrack_candidate = build_pending

    def original_build(attempts, *args, **kwargs):
        assert attempts == [old_attempt]
        return all_questions

    legacy.build_node_adaptive_session = original_build

    def original_start(uid, *args, **kwargs):
        selected = legacy.build_node_adaptive_session([old_attempt], 30)
        legacy.study_sessions[uid] = {
            "session_id": "session-1",
            "status": "waiting_for_answers",
            "current_set": 1,
            "question_count": 30,
            "questions_per_set": 5,
            "total_sets": 6,
            "questions": selected[:5],
            "all_questions": selected,
            "all_answers": {
                1: {"answer": "B", "confidence": "2"},
                2: {"answer": "A", "confidence": "1"},
                3: {"answer": "A", "confidence": "1"},
                4: {"answer": "A", "confidence": "1"},
                5: {"answer": "A", "confidence": "1"},
            },
            "mode": "study",
            "session_kind": "adaptive_daily",
        }
        return ["quiz"]

    legacy.start_quiz = original_start
    legacy.record_confirmed_learning_batch = lambda uid, session: True

    def original_queue(uid, session):
        legacy.db_queue_calls += 1
        return "db-fallback"

    legacy.queue_prerequisite_backtrack_for_next_set = original_queue
    return legacy, user_id


def test_pilot_reuses_selector_history_after_successful_persist():
    legacy, user_id = _legacy()
    install_prerequisite_attempt_cache(legacy)

    legacy.start_quiz(user_id, session_kind="adaptive_daily")
    session = legacy.study_sessions[user_id]
    assert legacy.record_confirmed_learning_batch(user_id, session) is True

    candidate = legacy.queue_prerequisite_backtrack_for_next_set(user_id, session)

    assert candidate["question_id"] == "Q260"
    assert session["pending_prerequisite_backtrack"]["question_id"] == "Q260"
    assert legacy.db_queue_calls == 0


def test_missing_cache_falls_back_to_original_queue():
    legacy, user_id = _legacy()
    install_prerequisite_attempt_cache(legacy)
    session = {
        "session_id": "session-1",
        "current_set": 1,
        "total_sets": 6,
        "questions_per_set": 5,
        "all_questions": [{"id": "Q386"}],
        "mode": "study",
        "session_kind": "adaptive_daily",
    }

    assert legacy.queue_prerequisite_backtrack_for_next_set(user_id, session) == "db-fallback"
    assert legacy.db_queue_calls == 1


def test_failed_duplicate_persist_is_not_added_to_cache():
    legacy, user_id = _legacy()
    legacy.record_confirmed_learning_batch = lambda uid, session: False
    install_prerequisite_attempt_cache(legacy)
    legacy.start_quiz(user_id, session_kind="adaptive_daily")
    session = legacy.study_sessions[user_id]

    assert legacy.record_confirmed_learning_batch(user_id, session) is False
    # Current event was not inserted, so cache is deliberately incomplete and
    # the queue must choose correctness-preserving DB fallback.
    assert legacy.queue_prerequisite_backtrack_for_next_set(user_id, session) == "db-fallback"
    assert legacy.db_queue_calls == 1
