from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

from initial_assessment_repeat_guard import install_initial_assessment_repeat_guard


NOW = datetime(2026, 9, 12, 0, tzinfo=timezone.utc)


def recent_attempt(question_id):
    return {
        "question_id": question_id,
        "answered_at": NOW - timedelta(hours=2),
        "answer_status": "answered",
    }


def make_legacy(attempts):
    calls = {"build": [], "start": []}

    def build_initial_assessment(question_count=30, *, exclude_ids=()):
        calls["build"].append((question_count, set(exclude_ids)))
        return ["built"]

    def start_quiz(user_id, session_kind=None, question_count=None, exclude_ids=None):
        calls["start"].append((user_id, session_kind, question_count, exclude_ids))
        if session_kind == "initial_assessment":
            return legacy.build_initial_assessment(question_count or 30)
        return "other"

    legacy = SimpleNamespace(
        start_quiz=start_quiz,
        build_initial_assessment=build_initial_assessment,
        get_question_attempts=lambda _user_id: list(attempts),
    )
    return legacy, calls


def test_initial_assessment_injects_recent_question_exclusions():
    legacy, calls = make_legacy([recent_attempt("Q1783")])
    install_initial_assessment_repeat_guard(legacy)

    assert legacy.start_quiz("learner", session_kind="initial_assessment", question_count=30) == ["built"]
    assert calls["build"] == [(30, {"Q1783"})]


def test_initial_assessment_merges_explicit_exclusions():
    legacy, calls = make_legacy([recent_attempt("Q1783")])
    install_initial_assessment_repeat_guard(legacy)

    legacy.start_quiz(
        "learner",
        session_kind="initial_assessment",
        question_count=30,
        exclude_ids={"Q9"},
    )

    assert calls["build"] == [(30, {"Q1783", "Q9"})]


def test_non_initial_paths_are_unchanged():
    legacy, calls = make_legacy([recent_attempt("Q1783")])
    install_initial_assessment_repeat_guard(legacy)

    assert legacy.start_quiz("learner", session_kind="adaptive_daily", question_count=30) == "other"
    assert calls["build"] == []


def test_installer_is_idempotent():
    legacy, _calls = make_legacy([])
    install_initial_assessment_repeat_guard(legacy)
    first_start = legacy.start_quiz
    first_build = legacy.build_initial_assessment

    install_initial_assessment_repeat_guard(legacy)

    assert legacy.start_quiz is first_start
    assert legacy.build_initial_assessment is first_build
