import pytest

from phase12_presentation import REASON_WORDING, build_phase12_presentation


def _shadow(reason_code, *, field="神経学", count=10, route="dashboard_recommendation"):
    return {
        "learning_intent": "repair",
        "target_field": field,
        "question_count": count,
        "recommended_route": route,
        "reason_code": reason_code,
        "evidence": ["critical_safety_node=KN9999"],
        "priority_score": 999,
    }


def _evidence():
    return {
        "canonical_node_evidence": [
            {"canonical_node_id": "KN0001", "state": "unseen"},
            {"canonical_node_id": "KN0002", "state": "checking"},
            {"canonical_node_id": "KN0003", "state": "repairing"},
            {"canonical_node_id": "KN0004", "state": "repaired"},
            {"canonical_node_id": "KN0005", "state": "recheck_due"},
            {"canonical_node_id": "KN0006", "state": "stable"},
        ]
    }


@pytest.mark.parametrize("reason_code,wording", REASON_WORDING.items())
def test_all_phase11_reasons_have_approved_learner_wording(reason_code, wording):
    result = build_phase12_presentation(_shadow(reason_code), _evidence())
    assert result["reason"] == wording
    assert result["headline"] == "今日は神経学を10問"


def test_presentation_has_canonical_state_counts_and_no_internal_evidence():
    result = build_phase12_presentation(_shadow("safety_repair"), _evidence())
    assert result["state_summary"] == {
        "unseen": 1, "checking": 1, "repairing": 1,
        "repaired": 1, "recheck_due": 1, "stable": 1,
    }
    serialized = str(result)
    assert "KN9999" not in serialized
    assert "priority_score" not in serialized
    assert len(result["attention_items"]) <= 3


def test_maintenance_uses_broad_headline_without_inventing_a_field():
    result = build_phase12_presentation(
        _shadow("maintenance_only", field=None, count=30, route="adaptive_daily"),
        _evidence(),
    )
    assert result["headline"] == "今日はおすすめ学習を30問"
    assert result["target_field"] is None
    assert result["attention_items"] == []


def test_unknown_reason_fails_closed():
    with pytest.raises(ValueError):
        build_phase12_presentation(_shadow("unknown_rule"), _evidence())
