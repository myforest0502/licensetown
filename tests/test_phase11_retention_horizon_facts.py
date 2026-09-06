from datetime import datetime, timedelta, timezone

from phase11_retention_horizon_facts import (
    build_retention_horizon_evidence_line,
    build_retention_horizon_facts,
)


NOW = datetime(2026, 9, 6, 8, 0, tzinfo=timezone.utc)


def test_summarizes_due_and_upcoming_reviews_without_mutation():
    states = [
        {"canonical_node_id": "KN1", "state": "recheck_due", "next_review_at": NOW - timedelta(hours=1)},
        {"canonical_node_id": "KN2", "state": "repaired", "next_review_at": NOW + timedelta(hours=12)},
        {"canonical_node_id": "KN3", "state": "repaired", "next_review_at": NOW + timedelta(days=2)},
        {"canonical_node_id": "KN4", "state": "stable", "next_review_at": NOW + timedelta(days=5)},
        {"canonical_node_id": "KN5", "state": "repairing", "next_review_at": NOW + timedelta(hours=2)},
        {"canonical_node_id": "KN6", "state": "repaired", "next_review_at": NOW + timedelta(days=10)},
    ]
    original = [dict(item) for item in states]

    facts = build_retention_horizon_facts(states, as_of=NOW)

    assert states == original
    assert facts["recheck_due_count"] == 1
    assert facts["upcoming_review_count"] == 4
    assert facts["due_within_24h_count"] == 1
    assert facts["due_within_3d_count"] == 2
    assert facts["due_within_7d_count"] == 3
    assert facts["earliest_review_in_hours"] == 12.0
    assert facts["earliest_review_at_jst"].startswith("2026-09-06T29") is False
    assert facts["diagnostic_only"] is True
    assert "manufacture attempts" in facts["policy_note"]


def test_empty_and_invalid_review_times_fail_closed():
    facts = build_retention_horizon_facts([
        {"canonical_node_id": "KN1", "state": "repaired", "next_review_at": None},
        {"canonical_node_id": "KN2", "state": "stable", "next_review_at": "not-a-time"},
    ], as_of=NOW)
    assert facts["recheck_due_count"] == 0
    assert facts["upcoming_review_count"] == 0
    assert facts["earliest_review_at_jst"] is None
    assert facts["earliest_review_in_hours"] is None


def test_evidence_line_is_non_identifying_and_has_safe_defaults():
    line = build_retention_horizon_evidence_line({
        "recheck_due_count": 0,
        "upcoming_review_count": 13,
        "due_within_24h_count": 0,
        "due_within_3d_count": 4,
        "due_within_7d_count": 13,
        "earliest_review_at_jst": "2026-09-09T08:26:32+09:00",
        "earliest_review_in_hours": 63.4,
        "user_id": "must-not-leak",
        "token": "must-not-leak",
    })
    assert line.startswith("retention_horizon=due_now:0,upcoming:13,within_24h:0,within_3d:4")
    assert "earliest_at_jst:2026-09-09T08:26:32+09:00" in line
    assert "must-not-leak" not in line
    assert "user_id" not in line
    assert "token" not in line
    assert build_retention_horizon_evidence_line(None) == (
        "retention_horizon=due_now:0,upcoming:0,within_24h:0,within_3d:0,within_7d:0,"
        "earliest_at_jst:none,earliest_in_hours:none"
    )
