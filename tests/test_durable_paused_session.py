from types import SimpleNamespace

import durable_paused_session as durable
from durable_paused_session import (
    DurableStudySessions,
    PausedSessionStore,
    install_durable_paused_sessions,
)


def setup_function():
    durable._local_snapshots.clear()


def teardown_function():
    durable._local_snapshots.clear()


class LocalDatabase:
    @staticmethod
    def database_is_available():
        return False


class FakeLegacy(SimpleNamespace):
    def __init__(self):
        super().__init__()
        self.study_sessions = {}

        def pause(user_id):
            session = self.study_sessions.get(user_id)
            if not session:
                return False
            if session.get("status") != "paused":
                session["resume_status"] = session.get("status", "waiting_for_answers")
            session.pop("active_started_at", None)
            session["status"] = "paused"
            return True

        def resume(user_id):
            session = self.study_sessions.get(user_id)
            if not session or session.get("status") != "paused":
                return None
            session["status"] = session.pop("resume_status", "waiting_for_answers")
            session["active_started_at"] = 999.0
            return session

        self.pause_quiz_session = pause
        self.resume_quiz_session = resume


def _session():
    return {
        "session_id": "session-1",
        "status": "waiting_for_continue",
        "current_set": 2,
        "question_count": 30,
        "questions_per_set": 5,
        "total_sets": 6,
        "questions": [{"id": "Q6"}],
        "all_questions": [{"id": f"Q{n}"} for n in range(1, 31)],
        "all_answers": {
            1: {"answer": "A", "confidence": "1"},
            2: {"answer": "B", "confidence": "2"},
        },
        "expected_numbers": [6, 7, 8, 9, 10],
        "mode": "study",
        "started_at": 100.0,
        "active_started_at": 200.0,
        "category_small": None,
        "session_kind": "random",
    }


def test_paused_snapshot_survives_recreated_in_memory_dict_and_restores_int_answer_keys():
    store = PausedSessionStore(LocalDatabase())
    snapshot = _session()
    snapshot["resume_status"] = snapshot["status"]
    snapshot["status"] = "paused"
    snapshot.pop("active_started_at", None)
    assert store.save("user", snapshot) is True

    restarted = DurableStudySessions({}, PausedSessionStore(LocalDatabase()))
    restored = restarted.get("user")

    assert restored is not None
    assert restored["status"] == "paused"
    assert restored["session_id"] == "session-1"
    assert restored["current_set"] == 2
    assert 1 in restored["all_answers"]
    assert "1" not in restored["all_answers"]


def test_install_pause_persists_then_process_restart_can_resume_exact_session():
    legacy = FakeLegacy()
    install_durable_paused_sessions(legacy, LocalDatabase())
    legacy.study_sessions["user"] = _session()

    assert legacy.pause_quiz_session("user") is True
    expected_questions = legacy.study_sessions["user"]["all_questions"]

    # Simulate a Render process restart: in-memory dict disappears, durable
    # storage remains. A fresh composition layer must lazily restore it.
    restarted = FakeLegacy()
    install_durable_paused_sessions(restarted, LocalDatabase())
    restored = restarted.study_sessions.get("user")

    assert restored is not None
    assert restored["status"] == "paused"
    assert restored["all_questions"] == expected_questions
    assert restarted.resume_quiz_session("user") is restored
    assert restored["status"] == "waiting_for_continue"
    assert restored["active_started_at"] == 999.0

    # Successful resume consumes the durable paused snapshot.
    restarted.study_sessions.clear()
    assert restarted.study_sessions.get("user") is None


def test_new_live_session_replaces_stale_paused_snapshot():
    store = PausedSessionStore(LocalDatabase())
    paused = _session()
    paused["status"] = "paused"
    paused["resume_status"] = "waiting_for_answers"
    paused.pop("active_started_at", None)
    assert store.save("user", paused)

    sessions = DurableStudySessions({}, store)
    sessions["user"] = {"session_id": "new", "status": "waiting_for_answers"}
    sessions.clear()

    assert store.load("user") is None


def test_pop_removes_durable_snapshot_for_finish_reset_or_start_over():
    store = PausedSessionStore(LocalDatabase())
    paused = _session()
    paused["status"] = "paused"
    paused["resume_status"] = "waiting_for_answers"
    paused.pop("active_started_at", None)
    assert store.save("user", paused)

    sessions = DurableStudySessions({}, store)
    assert sessions.get("user") is not None
    sessions.pop("user", None)

    fresh = DurableStudySessions({}, store)
    assert fresh.get("user") is None


def test_install_is_idempotent():
    legacy = FakeLegacy()
    install_durable_paused_sessions(legacy, LocalDatabase())
    sessions = legacy.study_sessions
    pause = legacy.pause_quiz_session

    install_durable_paused_sessions(legacy, LocalDatabase())

    assert legacy.study_sessions is sessions
    assert legacy.pause_quiz_session is pause
