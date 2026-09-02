import os

os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ.setdefault("CHANNEL_ACCESS_TOKEN", "test-token")
os.environ.setdefault("CHANNEL_SECRET", "test-secret")

from pilot_diagnostics import build_phase11_promotion_evidence_text


def _text(repair_supply):
    return build_phase11_promotion_evidence_text(
        period="all",
        shadow_judgment={"comparison": {"shadow_reason_profile_consistent": True}},
        repeat_structure_audit={},
        saved_adaptive_daily_audit={},
        retrospective_shadow_audit={},
        state_counts={},
        transitions={},
        repairing_node_repairability={},
        adaptive_count=0,
        adaptive_unique_questions=0,
        adaptive_unique_nodes=0,
        adaptive_groups={},
        strong_repair_supply_priorities=repair_supply,
    )


def test_bundle_exports_repair_supply_summary_and_ranked_top_details():
    supply = {
        "target_node_total": 2,
        "priority_counts": {"A": 1, "B": 1, "C": 0, "D": 0},
        "weak_pair_review_count": 1,
        "create_strong_alternate_count": 1,
        "top": [
            {
                "rank": 1,
                "canonical_node_id": "KN0008",
                "formal_label": "Safety node",
                "supply_priority_tier": "A",
                "supply_action": "create_strong_alternate",
                "safety_levels": ["moderate"],
                "current_cycle_wrong_count": 2,
                "confident_wrong_count": 1,
                "distinct_wrong_question_count": 1,
                "wrong_question_ids": ["Q8"],
                "all_question_ids": ["Q8"],
                "weak_repair_candidate_question_ids": [],
                "unseen_different_question_ids": [],
            },
            {
                "rank": 2,
                "canonical_node_id": "KN0609",
                "formal_label": "Internal medicine node",
                "supply_priority_tier": "B",
                "supply_action": "review_existing_weak_pair",
                "safety_levels": [],
                "current_cycle_wrong_count": 3,
                "confident_wrong_count": 2,
                "distinct_wrong_question_count": 2,
                "wrong_question_ids": ["Q617", "Q900"],
                "all_question_ids": ["Q617", "Q900", "Q1200"],
                "weak_repair_candidate_question_ids": ["Q1200"],
                "unseen_different_question_ids": ["Q1200"],
            },
        ],
    }
    text = _text(supply)
    assert "repair_supply=targets:2,priority_A:1,priority_B:1,priority_C:0,priority_D:0,weak_pair_review:1,create_strong_alternate:1" in text
    assert "repair_supply_top_1=node:KN0008,label:Safety node,tier:A,action:create_strong_alternate,safety:moderate" in text
    assert "cycle_wrong:2,confident_wrong:1,distinct_wrong_q:1,wrong_q:Q8,all_q:Q8" in text
    assert "weak_candidates:none,unseen_different_q:none" in text
    assert "repair_supply_top_2=node:KN0609,label:Internal medicine node,tier:B,action:review_existing_weak_pair,safety:none" in text
    assert "wrong_q:Q617|Q900,all_q:Q617|Q900|Q1200,weak_candidates:Q1200,unseen_different_q:Q1200" in text
    assert text.index("repair_supply_top_1=") < text.index("repair_supply_top_2=")


def test_bundle_repair_supply_defaults_are_safe_and_identity_free():
    text = _text({})
    assert "repair_supply=targets:0,priority_A:0,priority_B:0,priority_C:0,priority_D:0,weak_pair_review:0,create_strong_alternate:0" in text
    assert "repair_supply_top_" not in text
    lowered = text.lower()
    for forbidden in ("user_id", "learner_user_id", "supporter_token", "dashboard_token", "consultation"):
        assert forbidden not in lowered
