from datetime import datetime, timedelta, timezone

from knowledge_node_repair_cycle import (
    current_evaluable_repair_cycle,
    current_repair_cycle,
)


BASE = datetime(2026, 9, 1, tzinfo=timezone.utc)


def attempt(q, *, correct, confidence, when, unknown=False):
    return {
        "id": int(when.total_seconds()) + 1,
        "event_key": f"e-{q}-{when.total_seconds()}",
        "user_id": "u",
        "question_id": q,
        "knowledge_node_id": "KN0268",
        "selected_answers": [] if unknown else ["A"],
        "answer_status": "unknown" if unknown else "answered",
        "is_correct": correct,
        "confidence": confidence,
        "answered_at": BASE + when,
        "attempt_position": 1,
    }


def test_no_active_cycle_when_current_state_is_repaired():
    history = [
        attempt("Q269", correct=False, confidence=2, when=timedelta()),
        attempt("Q361", correct=True, confidence=1, when=timedelta(minutes=1)),
    ]
    assert current_repair_cycle(history, as_of=BASE + timedelta(days=1)) == []


def test_no_active_cycle_when_repaired_has_only_become_recheck_due_by_time():
    history = [
        attempt("Q269", correct=False, confidence=2, when=timedelta()),
        attempt("Q361", correct=True, confidence=1, when=timedelta(minutes=1)),
    ]
    assert current_repair_cycle(history, as_of=BASE + timedelta(days=8)) == []


def test_failed_due_check_starts_new_consecutive_repairing_run():
    first = attempt("Q269", correct=False, confidence=2, when=timedelta())
    repaired = attempt("Q361", correct=True, confidence=1, when=timedelta(minutes=1))
    failed_recheck = attempt("Q269", correct=False, confidence=2, when=timedelta(days=8))
    cycle = current_repair_cycle([first, repaired, failed_recheck])
    assert [item["question_id"] for item in cycle] == ["Q269"]
    assert cycle[0]["answered_at"] == failed_recheck["answered_at"]


def test_unknown_after_repaired_is_active_but_not_evaluable():
    first = attempt("Q269", correct=False, confidence=2, when=timedelta())
    repaired = attempt("Q361", correct=True, confidence=1, when=timedelta(minutes=1))
    unknown = attempt(
        "Q269", correct=False, confidence=None, when=timedelta(days=2), unknown=True
    )
    history = [first, repaired, unknown]
    assert [item["question_id"] for item in current_repair_cycle(history)] == ["Q269"]
    assert current_evaluable_repair_cycle(history) == []


def test_current_cycle_keeps_only_attempts_after_latest_repair_boundary():
    old_wrong = attempt("Q269", correct=False, confidence=1, when=timedelta())
    repaired = attempt("Q361", correct=True, confidence=1, when=timedelta(minutes=1))
    new_wrong = attempt("Q269", correct=False, confidence=2, when=timedelta(days=2))
    weak_correct = attempt("Q269", correct=True, confidence=1, when=timedelta(days=2, minutes=1))
    cycle = current_repair_cycle([old_wrong, repaired, new_wrong, weak_correct])
    assert [item["question_id"] for item in cycle] == ["Q269", "Q269"]
    assert old_wrong not in cycle
    assert repaired not in cycle


def test_initial_unrepaired_run_remains_whole_cycle():
    first = attempt("Q269", correct=False, confidence=2, when=timedelta())
    second = attempt("Q269", correct=True, confidence=1, when=timedelta(minutes=1))
    cycle = current_repair_cycle([first, second])
    assert [item["question_id"] for item in cycle] == ["Q269", "Q269"]
    assert len(current_evaluable_repair_cycle([first, second])) == 2
