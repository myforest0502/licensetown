import os
import random
from datetime import datetime, timedelta, timezone

os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ.setdefault("CHANNEL_ACCESS_TOKEN", "test-token")
os.environ.setdefault("CHANNEL_SECRET", "test-secret")

import adaptive_question_selector as selector
import app
from scripts.simulate_node_adaptive_recommendation import load_attempts_read_only


NOW = datetime(2026, 8, 29, tzinfo=timezone.utc)


def attempt(q, node, correct, confidence=2, *, user="u", minute=0, status="answered"):
    return {
        "user_id": user, "question_id": q, "knowledge_node_id": node,
        "is_correct": correct, "confidence": confidence,
        "answer_status": status, "answered_at": NOW + timedelta(minutes=minute),
        "event_key": f"e-{user}-{minute}", "attempt_position": 1,
    }


def fake_bank(monkeypatch, count=60, safety_by_node=None):
    ids = tuple(f"Q{i}" for i in range(1, count + 1))
    safety_by_node = safety_by_node or {}
    monkeypatch.setattr(selector, "question_ids", lambda: ids)
    monkeypatch.setattr(selector, "get_question_tag", lambda q: {
        "knowledge_node_id": f"KN{((int(q[1:]) - 1) // 2) + 1:04d}",
        "safety": safety_by_node.get(f"KN{((int(q[1:]) - 1) // 2) + 1:04d}", "none"),
    })
    return ids


def test_empty_history_includes_unseen_and_unique_questions(monkeypatch):
    fake_bank(monkeypatch)
    selected = selector.select_node_adaptive_questions([], 30, rng=random.Random(1))
    assert len(selected) == 30
    assert len({item["question_id"] for item in selected}) == 30
    assert all(item["state"] == "unseen" for item in selected)


def test_repairing_prefers_different_question_and_limits_node_concentration(monkeypatch):
    fake_bank(monkeypatch)
    monkeypatch.setattr(selector, "classify_repair_confirmation", lambda old, new: (
        "same_question" if old == new else "different_question_strong"
    ))
    selected = selector.select_node_adaptive_questions(
        [attempt("Q1", "KN0001", False)], 30, rng=random.Random(1)
    )
    node_items = [item for item in selected if item["canonical_node_id"] == "KN0001"]
    assert node_items[0]["question_id"] == "Q2"
    assert node_items[0]["same_question_repeat"] is False
    assert len(node_items) <= 2


def test_repaired_node_is_not_kept_in_high_priority_repair(monkeypatch):
    fake_bank(monkeypatch)
    monkeypatch.setattr(selector, "derive_all_user_node_states", lambda *_args, **_kwargs: [
        {"canonical_node_id": "KN0001", "state": "repaired"}
    ])
    selected = selector.select_node_adaptive_questions(
        [attempt("Q1", "KN0001", False)], 10, rng=random.Random(11)
    )
    node_items = [item for item in selected if item["canonical_node_id"] == "KN0001"]
    assert all(item["priority_group"] == "maintenance" for item in node_items)
    assert all(item["priority_reason"] == "repaired" for item in node_items)
    assert any(item["state"] == "unseen" for item in selected)


def test_priority_order_safety_confident_and_cross_wrong(monkeypatch):
    fake_bank(monkeypatch, safety_by_node={"KN0001": "critical"})
    attempts = [
        attempt("Q1", "KN0001", False, 2, minute=1),
        attempt("Q3", "KN0002", False, 1, minute=2),
        attempt("Q5", "KN0003", False, 2, minute=3),
        attempt("Q6", "KN0003", False, 2, minute=4),
    ]
    selected = selector.select_node_adaptive_questions(attempts, 10, rng=random.Random(2))
    reasons = [item["priority_reason"] for item in selected]
    assert reasons.index("safety_wrong") < reasons.index("confident_wrong")
    assert "cross_question_wrong" in reasons


def test_unknown_is_repairing_evidence(monkeypatch):
    fake_bank(monkeypatch)
    selected = selector.select_node_adaptive_questions([
        attempt("Q1", "KN0001", False, None, status="unknown")
    ], 10, rng=random.Random(3))
    node = next(item for item in selected if item["canonical_node_id"] == "KN0001")
    assert node["priority_reason"] == "repairing"
    assert node["unknown_evidence"] is True


def test_canonical_aliases_share_state(monkeypatch):
    fake_bank(monkeypatch)
    monkeypatch.setattr(selector, "get_question_tag", lambda q: {
        "knowledge_node_id": "KN0597" if q == "Q1" else ("KN0807" if q == "Q2" else f"KN{int(q[1:]):04d}"),
        "safety": "none",
    })
    selected = selector.select_node_adaptive_questions([
        attempt("Q1", "KN0597", False)
    ], 10, rng=random.Random(4))
    q2 = next(item for item in selected if item["question_id"] == "Q2")
    assert q2["canonical_node_id"] == "KN0597"
    assert q2["previous_wrong_count"] == 1


def test_repaired_and_checking_are_included_without_same_day_stable(monkeypatch):
    fake_bank(monkeypatch)
    monkeypatch.setattr(selector, "derive_all_user_node_states", lambda *_args, **_kwargs: [
        {"canonical_node_id": "KN0001", "state": "repaired"},
        {"canonical_node_id": "KN0003", "state": "checking"},
    ])
    old = NOW - timedelta(days=31)
    attempts = [
        {**attempt("Q1", "KN0001", False, 2, minute=1), "answered_at": old},
        {**attempt("Q2", "KN0001", True, 1, minute=2), "answered_at": old + timedelta(minutes=1)},
        {**attempt("Q3", "KN0001", True, 1, minute=3), "answered_at": old + timedelta(minutes=2)},
        attempt("Q5", "KN0003", True, 1, minute=4),
    ]
    selected = selector.select_node_adaptive_questions(attempts, 20, rng=random.Random(5), as_of=NOW)
    assert not any(item["state"] in {"stable", "recheck_due"} for item in selected)
    assert not any(
        item["state"] == "repaired" and item["priority_group"] == "repair"
        for item in selected
    )
    assert any(item["state"] == "checking" for item in selected)


def test_stable_does_not_fill_session_when_unseen_exists(monkeypatch):
    fake_bank(monkeypatch)
    attempts = [
        attempt("Q1", "KN0001", False, 2, minute=1),
        attempt("Q2", "KN0001", True, 1, minute=2),
        attempt("Q3", "KN0001", True, 1, minute=3),
    ]
    selected = selector.select_node_adaptive_questions(attempts, 20, rng=random.Random(6))
    assert sum(item["state"] == "stable" for item in selected) < 20
    assert any(item["state"] == "unseen" for item in selected)


def test_small_candidate_bank_returns_available_without_duplicates(monkeypatch):
    fake_bank(monkeypatch, count=7)
    selected = selector.select_node_adaptive_questions([], 30, rng=random.Random(7))
    assert len(selected) == 7
    assert len({item["question_id"] for item in selected}) == 7


def test_exclusions_are_respected(monkeypatch):
    fake_bank(monkeypatch)
    selected = selector.select_node_adaptive_questions([], 10, exclude_ids={"Q1", "Q2"}, rng=random.Random(8))
    assert not ({"Q1", "Q2"} & {item["question_id"] for item in selected})


def test_exclude_ids_accepts_none_and_empty_iterables(monkeypatch):
    fake_bank(monkeypatch)
    for excluded in (None, (), []):
        selected = selector.select_node_adaptive_questions(
            [], 30, exclude_ids=excluded, rng=random.Random(8)
        )
        assert len(selected) == 30
        assert len({item["question_id"] for item in selected}) == 30


def test_user_histories_cannot_be_mixed(monkeypatch):
    fake_bank(monkeypatch)
    try:
        selector.select_node_adaptive_questions([
            attempt("Q1", "KN0001", False, user="a"),
            attempt("Q2", "KN0001", True, user="b"),
        ], 10)
    except ValueError as exc:
        assert "one user" in str(exc)
    else:
        raise AssertionError("mixed users must be rejected")


def test_flag_false_uses_legacy_without_attempt_db_read(monkeypatch):
    legacy = [{"id": f"Q{i}"} for i in range(1, 31)]
    monkeypatch.setattr(app, "ENABLE_NODE_ADAPTIVE_RECOMMENDATION", False)
    monkeypatch.setattr(app, "NODE_ADAPTIVE_RECOMMENDATION_PILOT_USER_IDS", {"flag-off"})
    monkeypatch.setattr(app, "get_question_history", lambda _u: [])
    monkeypatch.setattr(app, "build_daily_session", lambda *args, **kwargs: legacy)
    monkeypatch.setattr(app, "format_quiz_messages", lambda _questions: ["quiz"])
    monkeypatch.setattr(app, "get_question_attempts", lambda _u: (_ for _ in ()).throw(AssertionError("extra DB read")))
    app.user_modes["flag-off"] = "study"
    app.start_quiz("flag-off", session_kind="adaptive_daily")
    assert app.study_sessions["flag-off"]["all_questions"] == legacy
    app.study_sessions.pop("flag-off", None)


def test_flag_true_uses_node_selector(monkeypatch):
    adaptive = [{"id": f"Q{i}"} for i in range(1, 31)]
    monkeypatch.setattr(app, "ENABLE_NODE_ADAPTIVE_RECOMMENDATION", True)
    monkeypatch.setattr(app, "NODE_ADAPTIVE_RECOMMENDATION_PILOT_USER_IDS", {"flag-on"})
    monkeypatch.setattr(app, "get_question_attempts", lambda _u: [{"question_id": "Q1"}])
    monkeypatch.setattr(app, "build_node_adaptive_session", lambda *args, **kwargs: adaptive)
    monkeypatch.setattr(app, "format_quiz_messages", lambda _questions: ["quiz"])
    app.user_modes["flag-on"] = "study"
    app.start_quiz("flag-on", session_kind="adaptive_daily")
    assert app.study_sessions["flag-on"]["all_questions"] == adaptive
    app.study_sessions.pop("flag-on", None)


def test_node_adaptive_allowlist_parser_trims_deduplicates_and_drops_empty():
    assert selector.parse_node_adaptive_pilot_user_ids("abc, def,abc, ,") == {
        "abc", "def"
    }
    assert selector.parse_node_adaptive_pilot_user_ids(None) == set()


def test_node_adaptive_allowlist_is_fail_closed():
    enabled = selector.is_node_adaptive_recommendation_enabled
    assert not enabled(False, "son", {"son"})
    assert not enabled(True, "son", set())
    assert not enabled(True, "son", selector.parse_node_adaptive_pilot_user_ids(None))
    assert not enabled(True, "other", {"son"})
    assert enabled(True, "son", {"son", "other"})


def test_flag_true_non_allowlisted_user_preserves_legacy_and_no_attempt_read(monkeypatch):
    legacy = [{"id": f"Q{i}"} for i in range(1, 31)]
    monkeypatch.setattr(app, "ENABLE_NODE_ADAPTIVE_RECOMMENDATION", True)
    monkeypatch.setattr(app, "NODE_ADAPTIVE_RECOMMENDATION_PILOT_USER_IDS", {"son"})
    monkeypatch.setattr(app, "get_question_history", lambda _u: [])
    monkeypatch.setattr(app, "build_daily_session", lambda *args, **kwargs: legacy)
    monkeypatch.setattr(app, "format_quiz_messages", lambda _questions: ["quiz"])
    monkeypatch.setattr(app, "get_question_attempts", lambda _u: (_ for _ in ()).throw(AssertionError("extra DB read")))
    app.user_modes["not-son"] = "study"
    app.start_quiz("not-son", session_kind="adaptive_daily")
    assert app.study_sessions["not-son"]["all_questions"] == legacy
    app.study_sessions.pop("not-son", None)


class Cursor:
    def __init__(self):
        self.sql = ""
    def __enter__(self): return self
    def __exit__(self, *_): return False
    def execute(self, sql): self.sql = " ".join(sql.split())
    def fetchall(self): return []


class Connection:
    def __init__(self): self.value = Cursor()
    def cursor(self): return self.value


def test_production_simulation_loader_is_select_only():
    connection = Connection()
    assert load_attempts_read_only(connection) == []
    assert connection.value.sql.startswith("SELECT ")
    assert not any(word in connection.value.sql.upper() for word in (
        "INSERT", "UPDATE", "DELETE", "TRUNCATE", "ALTER", "CREATE", "DROP"
    ))
