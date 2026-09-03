import os
from datetime import datetime, timezone

os.environ.setdefault("OPENAI_API_KEY", "x")
os.environ.setdefault("CHANNEL_ACCESS_TOKEN", "x")
os.environ.setdefault("CHANNEL_SECRET", "x")

import database
from adaptive_question_selector import select_node_adaptive_questions
from app import app
from knowledge_node_repairability import build_repairability_audit
from repairability_diagnostics import (
    FORMALLY_BLOCKED,
    STRONG_AVAILABLE,
    WEAK_ONLY,
    build_repairing_node_repairability,
    build_strong_repair_supply_priorities,
)


NOW = datetime(2026, 9, 2, tzinfo=timezone.utc)


def _wrong(question_id, node_id, *, confidence=2, unknown=False, user="learner"):
    return {
        "event_key": f"{question_id}:1", "user_id": user,
        "question_id": question_id, "knowledge_node_id": node_id,
        "selected_answers": [] if unknown else ["A"], "is_correct": False,
        "confidence": None if unknown else confidence,
        "answer_status": "unknown" if unknown else "answered",
        "answered_at": NOW, "attempt_position": 1,
    }


def _records_by_classification():
    records = build_repairability_audit()
    strong = next(item for item in records if item["strong_alt_pairs"])
    weak = next(item for item in records if not item["strong_alt_pairs"] and item["weak_alt_pairs"])
    same = next(item for item in records if len(item["question_ids"]) == 1)
    return records, strong, weak, same


def setup_function():
    database._local_question_attempts.clear()
    database._local_learning_events.clear()
    database._local_supporter_links.clear()


def test_only_repairing_nodes_are_classified_and_all_buckets_balance():
    records, strong, weak, same = _records_by_classification()
    attempts = [
        _wrong(strong["question_ids"][0], strong["canonical_node_id"]),
        _wrong(weak["question_ids"][0], weak["canonical_node_id"]),
        _wrong(same["question_ids"][0], same["canonical_node_id"]),
    ]
    result = build_repairing_node_repairability(
        attempts, as_of=NOW, repairability_records=records,
    )
    assert result["repairing_node_total"] == 3
    assert result["strong_available_count"] == 1
    assert result["weak_only_count"] == 1
    assert result["same_or_blocked_count"] == 1
    assert sum((result["strong_available_count"], result["weak_only_count"], result["same_or_blocked_count"])) == 3
    by_node = {item["canonical_node_id"]: item for item in result["details"]}
    assert by_node[strong["canonical_node_id"]]["classification"] == STRONG_AVAILABLE
    assert by_node[strong["canonical_node_id"]]["strong_repair_candidate_question_ids"]
    assert by_node[weak["canonical_node_id"]]["classification"] == WEAK_ONLY
    assert by_node[same["canonical_node_id"]]["classification"] == FORMALLY_BLOCKED


def test_unknown_can_create_formal_repairing_state_but_not_wrong_evidence():
    records, strong, _weak, _same = _records_by_classification()
    result = build_repairing_node_repairability(
        [_wrong(strong["question_ids"][0], strong["canonical_node_id"], unknown=True)],
        as_of=NOW,
        repairability_records=records,
    )
    assert result["repairing_node_total"] == 1
    item = result["details"][0]
    assert item["wrong_question_ids"] == []
    assert item["strong_repair_candidate_question_ids"] == []
    assert item["classification"] == FORMALLY_BLOCKED


def test_canonical_alias_is_grouped_and_safety_uses_normal_classification():
    records = build_repairability_audit()
    record = next(item for item in records if item["canonical_node_id"] == "KN0597")
    result = build_repairing_node_repairability(
        [_wrong(record["question_ids"][0], "KN0807")],
        as_of=NOW,
        repairability_records=records,
    )
    assert result["details"][0]["canonical_node_id"] == "KN0597"
    safety_record = next(item for item in records if any(v != "none" for v in item["safety"]))
    safety = build_repairing_node_repairability(
        [_wrong(safety_record["question_ids"][0], safety_record["canonical_node_id"])],
        as_of=NOW,
        repairability_records=records,
    )["details"][0]
    assert safety["safety"] is True
    assert safety["classification"] in {STRONG_AVAILABLE, WEAK_ONLY, FORMALLY_BLOCKED}


def test_helper_does_not_mutate_attempts_or_selector_results():
    records, strong, _weak, _same = _records_by_classification()
    attempts = [_wrong(strong["question_ids"][0], strong["canonical_node_id"])]
    original = [dict(item) for item in attempts]
    before = select_node_adaptive_questions(attempts, 5, rng=__import__("random").Random(7), as_of=NOW)
    build_repairing_node_repairability(attempts, as_of=NOW, repairability_records=records)
    after = select_node_adaptive_questions(attempts, 5, rng=__import__("random").Random(7), as_of=NOW)
    assert attempts == original
    assert before == after


def test_internal_route_displays_details_but_learner_route_does_not(monkeypatch):
    records, strong, _weak, _same = _records_by_classification()
    database._local_question_attempts.append(
        _wrong(strong["question_ids"][0], strong["canonical_node_id"])
    )
    monkeypatch.setenv("LT_INTERNAL_ADMIN_TOKEN", "admin-secret")
    client = app.test_client()
    html = client.get(
        "/internal/pilot-diagnostics?token=admin-secret&learner_user_id=learner"
    ).get_data(as_text=True)
    assert "修復中Nodeの修復可能性" in html
    assert "strong repair問題 整備優先順位" in html
    assert strong["canonical_node_id"] in html
    assert "strong repair候補Q" in html
    learner = client.get("/goukaku-no-michi?token=invalid").get_data(as_text=True)
    assert "修復中Nodeの修復可能性" not in learner
    assert "strong repair問題 整備優先順位" not in learner


def _priority_item(node, classification, *, safety=(), confident=0, wrong=1, distinct=1):
    return {
        "canonical_node_id": node,
        "formal_label": node,
        "current_state": "repairing",
        "classification": classification,
        "safety": bool(safety),
        "safety_levels": list(safety),
        "confident_wrong_count": confident,
        "current_cycle_wrong_count": wrong,
        "distinct_wrong_question_count": distinct,
        "answered_question_ids": ["Q1"], "wrong_question_ids": ["Q1"],
        "all_question_ids": ["Q1"], "unseen_different_question_ids": [],
        "strong_repair_candidate_question_ids": [],
        "weak_repair_candidate_question_ids": [],
    }


def test_supply_priority_excludes_strong_and_orders_explicit_tiers():
    details = [
        _priority_item("KN0001", STRONG_AVAILABLE, safety=("critical",)),
        _priority_item("KN0002", FORMALLY_BLOCKED, safety=("moderate",)),
        _priority_item("KN0003", FORMALLY_BLOCKED, safety=("critical",)),
        _priority_item("KN0004", FORMALLY_BLOCKED, confident=2),
        _priority_item("KN0005", FORMALLY_BLOCKED, confident=1),
        _priority_item("KN0006", FORMALLY_BLOCKED, confident=0),
    ]
    result = build_strong_repair_supply_priorities({"details": details})
    assert [item["canonical_node_id"] for item in result["details"]] == [
        "KN0003", "KN0002", "KN0004", "KN0005", "KN0006",
    ]
    assert result["priority_counts"] == {"A": 2, "B": 1, "C": 1, "D": 1}
    assert result["target_node_total"] == 5


def test_weak_and_blocked_supply_actions_and_within_tier_order_are_deterministic():
    details = [
        _priority_item("KN0003", FORMALLY_BLOCKED, wrong=2, distinct=2),
        _priority_item("KN0002", WEAK_ONLY, wrong=3, distinct=1),
        _priority_item("KN0001", FORMALLY_BLOCKED, wrong=2, distinct=2),
    ]
    first = build_strong_repair_supply_priorities({"details": details}, top_limit=2)
    second = build_strong_repair_supply_priorities({"details": details}, top_limit=2)
    assert first == second
    assert [item["canonical_node_id"] for item in first["details"]] == [
        "KN0002", "KN0001", "KN0003",
    ]
    assert first["details"][0]["supply_action"] == "review_existing_weak_pair"
    assert first["details"][1]["supply_action"] == "create_strong_alternate"
    assert len(first["top"]) == 2
