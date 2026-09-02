from datetime import datetime, timezone

import pilot_diagnostics
from pilot_diagnostics import build_confident_wrong_node_details
from question_bank import CATEGORY_NAMES


NOW = datetime(2026, 9, 2, 1, 0, tzinfo=timezone.utc)


def _field_evidence(*nodes):
    return {
        "canonical_node_evidence": [
            {"canonical_node_id": node, "state": "repairing"} for node in nodes
        ]
    }


def _shadow(field_id=8, reason="confident_wrong_cluster"):
    return {"reason_code": reason, "target_field": CATEGORY_NAMES[field_id]}


def test_old_confident_history_does_not_leak_into_new_nonconfident_cycle(monkeypatch):
    monkeypatch.setattr(pilot_diagnostics, "get_category_small", lambda q: 8)
    monkeypatch.setattr(
        pilot_diagnostics,
        "build_active_repair_weakness",
        lambda attempts, as_of=None: {
            "KN0001": {
                "active_evaluable_wrong_question_ids": ["Q2"],
                "active_confident_wrong_question_ids": [],
                "active_confident_wrong_count": 0,
                "active_evaluable_wrong_question_count": 1,
                "active_weakness_evidence_level": "SINGLE_WRONG",
                "active_last_evaluable_wrong_at": NOW,
            }
        },
    )
    attempts = [
        {"question_id": "Q1", "knowledge_node_id": "KN0001", "is_correct": False, "confidence": 1},
        {"question_id": "Q2", "knowledge_node_id": "KN0001", "is_correct": False, "confidence": 2},
    ]
    assert build_confident_wrong_node_details(
        attempts, _field_evidence("KN0001"), _shadow(), as_of=NOW
    ) == []


def test_active_confident_wrong_detail_uses_active_counts_only(monkeypatch):
    monkeypatch.setattr(pilot_diagnostics, "get_category_small", lambda q: 8)
    monkeypatch.setattr(
        pilot_diagnostics,
        "build_active_repair_weakness",
        lambda attempts, as_of=None: {
            "KN0001": {
                "active_evaluable_wrong_question_ids": ["Q20", "Q3"],
                "active_confident_wrong_question_ids": ["Q20"],
                "active_confident_wrong_count": 1,
                "active_evaluable_wrong_question_count": 2,
                "active_weakness_evidence_level": "CROSS_QUESTION_CONFIDENT_WRONG",
                "active_last_evaluable_wrong_at": NOW,
            }
        },
    )
    details = build_confident_wrong_node_details(
        [], _field_evidence("KN0001"), _shadow(), as_of=NOW
    )
    assert len(details) == 1
    assert details[0]["question_ids"] == ["Q3", "Q20"]
    assert details[0]["confident_wrong_count"] == 1
    assert details[0]["distinct_question_count"] == 2
    assert details[0]["cross_question"] is True


def test_cross_confident_node_is_attributed_to_other_active_wrong_source_field(monkeypatch):
    fields = {"Q1": 8, "Q2": 9}
    monkeypatch.setattr(pilot_diagnostics, "get_category_small", lambda q: fields[q])
    monkeypatch.setattr(
        pilot_diagnostics,
        "build_active_repair_weakness",
        lambda attempts, as_of=None: {
            "KN0001": {
                "active_evaluable_wrong_question_ids": ["Q1", "Q2"],
                "active_confident_wrong_question_ids": ["Q1"],
                "active_confident_wrong_count": 1,
                "active_evaluable_wrong_question_count": 2,
                "active_weakness_evidence_level": "CROSS_QUESTION_CONFIDENT_WRONG",
                "active_last_evaluable_wrong_at": NOW,
            }
        },
    )
    details = build_confident_wrong_node_details(
        [], _field_evidence("KN0001"), _shadow(field_id=9), as_of=NOW
    )
    assert [item["canonical_node_id"] for item in details] == ["KN0001"]


def test_non_j2_shadow_returns_empty_without_active_evidence_call(monkeypatch):
    def fail(*args, **kwargs):
        raise AssertionError("active evidence should not be queried")

    monkeypatch.setattr(pilot_diagnostics, "build_active_repair_weakness", fail)
    assert build_confident_wrong_node_details(
        [], {}, _shadow(reason="insufficient_coverage"), as_of=NOW
    ) == []
