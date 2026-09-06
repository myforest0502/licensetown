from phase11_retention_supply_audit import (
    NO_ALTERNATE,
    STRONG_AVAILABLE,
    WEAK_ONLY,
    build_retention_supply_audit,
    build_retention_supply_evidence_line,
)


def registry():
    return [
        {"canonical_node_id": "KN1", "question_ids": ["Q1", "Q2"]},
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


def test_classifies_strong_weak_and_missing_supply(monkeypatch):
    def classify(old, new):
        if (old, new) == ("Q1", "Q2"):
            return "different_question_strong"
        if (old, new) == ("Q3", "Q4"):
            return "different_question_weak"
        return "same_question"

    monkeypatch.setattr(
        "phase11_retention_supply_audit.classify_repair_confirmation", classify
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


def test_due_without_strong_is_visible_and_not_falsely_clear(monkeypatch):
    monkeypatch.setattr(
        "phase11_retention_supply_audit.classify_repair_confirmation",
        lambda old, new: "different_question_weak",
    )
    result = build_retention_supply_audit(
        [states()[0]], repairability_records=registry()
    )
    assert result["due_node_count"] == 1
    assert result["due_without_strong_count"] == 1
    assert result["all_due_have_strong_supply"] is False


def test_no_due_nodes_does_not_claim_all_due_supply_is_verified(monkeypatch):
    monkeypatch.setattr(
        "phase11_retention_supply_audit.classify_repair_confirmation",
        lambda old, new: "different_question_strong",
    )
    result = build_retention_supply_audit(
        [states()[1]], repairability_records=registry()
    )
    assert result["due_node_count"] == 0
    assert result["all_due_have_strong_supply"] is False


def test_evidence_line_is_aggregate_only(monkeypatch):
    monkeypatch.setattr(
        "phase11_retention_supply_audit.classify_repair_confirmation",
        lambda old, new: "different_question_strong",
    )
    result = build_retention_supply_audit(
        [states()[0]], repairability_records=registry()
    )
    line = build_retention_supply_evidence_line(result)
    assert line.startswith("retention_supply=nodes:1,due:1,due_strong:1")
    assert "KN1" not in line
    assert "Q1" not in line
