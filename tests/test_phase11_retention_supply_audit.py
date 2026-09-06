from datetime import datetime, timedelta, timezone

from phase11_retention_supply_audit import (
    NO_ALTERNATE,
    STRONG_AVAILABLE,
    WEAK_ONLY,
    build_retention_supply_audit,
    build_retention_supply_evidence_line,
)


BASE = datetime(2026, 9, 6, tzinfo=timezone.utc)


def registry():
    return [
        {"canonical_node_id": "KN1", "question_ids": ["Q1", "Q2", "Q6"]},
        {"canonical_node_id": "KN2", "question_ids": ["Q3", "Q4"]},
        {"canonical_node_id": "KN3", "question_ids": ["Q5"]},
    ]


def states():
    return [
        {
            "canonical_node_id": "KN1",
            "state": "recheck_due",
            "retention_reference_question_id": "Q1",
            "next_review_at": "2026-09-09T00:00:00+00:00",
        },
        {
            "canonical_node_id": "KN2",
            "state": "repaired",
            "retention_reference_question_id": "Q3",
            "next_review_at": "2026-09-13T00:00:00+00:00",
        },
        {
            "canonical_node_id": "KN3",
            "state": "stable",
            "retention_reference_question_id": "Q5",
            "next_review_at": "2026-10-01T00:00:00+00:00",
        },
        {"canonical_node_id": "KNX", "state": "repairing"},
    ]


def attempt(q, minutes):
    return {
        "question_id": q,
        "answered_at": BASE + timedelta(minutes=minutes),
        "event_key": f"e-{minutes}-{q}",
        "attempt_position": 1,
    }


def classifier(old, new):
    if (old, new) in {("Q1", "Q2"), ("Q1", "Q6")}:
        return "different_question_strong"
    if (old, new) == ("Q3", "Q4"):
        return "different_question_weak"
    return "same_question"


def test_classifies_strong_weak_and_missing_supply(monkeypatch):
    monkeypatch.setattr(
        "phase11_retention_supply_audit.classify_repair_confirmation", classifier
    )
    result = build_retention_supply_audit(states(), repairability_records=registry())
    by_node = {item["canonical_node_id"]: item for item in result["details"]}

    assert by_node["KN1"]["classification"] == STRONG_AVAILABLE
    assert by_node["KN2"]["classification"] == WEAK_ONLY
    assert by_node["KN3"]["classification"] == NO_ALTERNATE
    assert result["due_node_count"] == 1
    assert result["due_strong_available_count"] == 1
    assert result["due_without_strong_count"] == 0
    assert result["upcoming_without_strong_count"] == 1
    assert result["all_due_have_strong_supply"] is True
    assert result["cooldown_known"] is False
    assert result["due_without_non_recent_strong_count"] is None


def test_cooldown_preflight_distinguishes_recent_from_non_recent_strong(monkeypatch):
    monkeypatch.setattr(
        "phase11_retention_supply_audit.classify_repair_confirmation", classifier
    )
    # Q2 is recent, but Q6 is not, so J4 has one immediately non-recent STRONG option.
    history = [attempt(f"QX{i}", i) for i in range(29)] + [attempt("Q2", 29)]
    result = build_retention_supply_audit(
        [states()[0]], attempts=history, repairability_records=registry()
    )
    detail = result["details"][0]
    assert detail["recent_strong_candidate_question_ids"] == ["Q2"]
    assert detail["non_recent_strong_candidate_question_ids"] == ["Q6"]
    assert result["due_non_recent_strong_available_count"] == 1
    assert result["due_without_non_recent_strong_count"] == 0
    assert result["cooldown_constrained_strong_node_count"] == 0


def test_all_strong_candidates_recent_is_visible_as_cooldown_constrained(monkeypatch):
    monkeypatch.setattr(
        "phase11_retention_supply_audit.classify_repair_confirmation", classifier
    )
    history = [attempt(f"QX{i}", i) for i in range(28)] + [
        attempt("Q2", 28),
        attempt("Q6", 29),
    ]
    result = build_retention_supply_audit(
        [states()[0]], attempts=history, repairability_records=registry()
    )
    assert result["due_strong_available_count"] == 1
    assert result["due_non_recent_strong_available_count"] == 0
    assert result["due_without_non_recent_strong_count"] == 1
    assert result["cooldown_constrained_strong_node_count"] == 1
    assert result["details"][0]["strong_supply_currently_cooldown_constrained"] is True


def test_due_without_strong_is_visible_and_not_falsely_clear(monkeypatch):
    monkeypatch.setattr(
        "phase11_retention_supply_audit.classify_repair_confirmation",
        lambda old, new: "different_question_weak",
    )
    result = build_retention_supply_audit(
        [states()[0]], attempts=[], repairability_records=registry()
    )
    assert result["due_node_count"] == 1
    assert result["due_without_strong_count"] == 1
    assert result["due_without_non_recent_strong_count"] == 1
    assert result["all_due_have_strong_supply"] is False


def test_no_due_nodes_does_not_claim_all_due_supply_is_verified(monkeypatch):
    monkeypatch.setattr(
        "phase11_retention_supply_audit.classify_repair_confirmation",
        lambda old, new: "different_question_strong",
    )
    result = build_retention_supply_audit(
        [states()[1]], attempts=[], repairability_records=registry()
    )
    assert result["due_node_count"] == 0
    assert result["all_due_have_strong_supply"] is False


def test_evidence_line_is_aggregate_only(monkeypatch):
    monkeypatch.setattr(
        "phase11_retention_supply_audit.classify_repair_confirmation", classifier
    )
    result = build_retention_supply_audit(
        [states()[0]], attempts=[attempt("Q2", 1)], repairability_records=registry()
    )
    line = build_retention_supply_evidence_line(result)
    assert line.startswith("retention_supply=nodes:1,due:1,due_strong:1")
    assert "cooldown_known:1" in line
    assert "due_nonrecent_strong:1" in line
    assert "KN1" not in line
    assert "Q1" not in line
