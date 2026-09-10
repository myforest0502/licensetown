from types import SimpleNamespace

import durable_web_learning_session as module
from durable_web_learning_session import (
    DurableWebLearningSessions,
    WebLearningSessionStore,
    install_durable_web_learning_sessions,
)


def setup_function():
    module._local_snapshots.clear()


def teardown_function():
    module._local_snapshots.clear()


def _database_off():
    return SimpleNamespace(database_is_available=lambda: False)


def _session(user_id="user", current_index=0, completed=False):
    return {
        "user_id": user_id,
        "dashboard_token": "token",
        "category_small": 8,
        "question_count": 10,
        "questions": [{"id": f"Q{n}"} for n in range(1, 11)],
        "selection_audit": {},
        "current_index": current_index,
        "correct_count": current_index,
        "completed": completed,
        "started_at": 123.5,
    }


def test_mapping_persists_new_session_and_restores_after_process_rebuild():
    store = WebLearningSessionStore(_database_off())
    first = DurableWebLearningSessions({}, store)
    first["sid"] = _session(current_index=3)

    rebuilt = DurableWebLearningSessions({}, WebLearningSessionStore(_database_off()))
    restored = rebuilt.get("sid")

    assert restored is not None
    assert restored["current_index"] == 3
    assert [q["id"] for q in restored["questions"]] == [f"Q{n}" for n in range(1, 11)]


def test_persist_saves_in_place_answer_progress_for_restart():
    durable = DurableWebLearningSessions({}, WebLearningSessionStore(_database_off()))
    durable["sid"] = _session()
    durable["sid"]["current_index"] = 4
    durable["sid"]["correct_count"] = 2
    assert durable.persist("sid") is True

    rebuilt = DurableWebLearningSessions({}, WebLearningSessionStore(_database_off()))
    assert rebuilt["sid"]["current_index"] == 4
    assert rebuilt["sid"]["correct_count"] == 2


def test_completed_session_remains_available_for_final_page_refresh():
    durable = DurableWebLearningSessions({}, WebLearningSessionStore(_database_off()))
    durable["sid"] = _session(current_index=10, completed=True)

    rebuilt = DurableWebLearningSessions({}, WebLearningSessionStore(_database_off()))
    assert rebuilt["sid"]["completed"] is True
    assert rebuilt["sid"]["current_index"] == 10


def test_pop_removes_persisted_session():
    durable = DurableWebLearningSessions({}, WebLearningSessionStore(_database_off()))
    durable["sid"] = _session()
    durable.pop("sid")

    rebuilt = DurableWebLearningSessions({}, WebLearningSessionStore(_database_off()))
    assert rebuilt.get("sid") is None


class _FakeApp:
    def __init__(self, answer):
        self.view_functions = {"answer_web_recommendation": answer}


def test_install_wraps_answer_endpoint_and_persists_mutated_progress():
    sessions = {}

    def answer(session_id):
        session = legacy.web_recommendation_sessions.get(session_id)
        session["current_index"] += 1
        session["correct_count"] += 1
        return {"ok": True}

    legacy = SimpleNamespace(
        web_recommendation_sessions=sessions,
        app=_FakeApp(answer),
        answer_web_recommendation=answer,
    )
    database = _database_off()

    install_durable_web_learning_sessions(legacy, database)
    legacy.web_recommendation_sessions["sid"] = _session()
    response = legacy.app.view_functions["answer_web_recommendation"]("sid")

    assert response == {"ok": True}
    rebuilt = DurableWebLearningSessions({}, WebLearningSessionStore(database))
    assert rebuilt["sid"]["current_index"] == 1
    assert rebuilt["sid"]["correct_count"] == 1


def test_install_is_idempotent():
    def answer(_session_id):
        return {"ok": True}

    legacy = SimpleNamespace(
        web_recommendation_sessions={},
        app=_FakeApp(answer),
        answer_web_recommendation=answer,
    )
    database = _database_off()
    install_durable_web_learning_sessions(legacy, database)
    first_mapping = legacy.web_recommendation_sessions
    first_endpoint = legacy.app.view_functions["answer_web_recommendation"]

    install_durable_web_learning_sessions(legacy, database)
    assert legacy.web_recommendation_sessions is first_mapping
    assert legacy.app.view_functions["answer_web_recommendation"] is first_endpoint
