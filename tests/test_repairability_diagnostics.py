import os
from datetime import datetime, timezone

os.environ.setdefault("OPENAI_API_KEY", "x")
os.environ.setdefault("CHANNEL_ACCESS_TOKEN", "x")
os.environ.setdefault("CHANNEL_SECRET", "x")

import database
from adaptive_question_selector import select_node_adaptive_questions
from app import app
from goukaku_ui import create_supporter_token
from knowledge_node_repairability import build_repairability_audit
from repairability_diagnostics import (
    FORMALLY_BLOCKED,
    STRONG_AVAILABLE,
    WEAK_ONLY,
    build_repairing_node_repairability,
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


def test_supporter_route_displays_details_but_learner_route_does_not():
    records, strong, _weak, _same = _records_by_classification()
    database._local_question_attempts.append(
        _wrong(strong["question_ids"][0], strong["canonical_node_id"])
    )
    database.set_supporter_link("supporter", "learner")
    token = create_supporter_token("supporter")
    client = app.test_client()
    html = client.get(
        f"/supporter/pilot-diagnostics?token={token}&learner_user_id=learner"
    ).get_data(as_text=True)
    assert "修復中Nodeの修復可能性" in html
    assert strong["canonical_node_id"] in html
    assert "strong repair候補Q" in html
    learner = client.get("/goukaku-no-michi?token=invalid").get_data(as_text=True)
    assert "修復中Nodeの修復可能性" not in learner
