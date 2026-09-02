import os

os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ.setdefault("CHANNEL_ACCESS_TOKEN", "test-token")
os.environ.setdefault("CHANNEL_SECRET", "test-secret")

from app import app
import goukaku_ui
from pilot_diagnostics import build_phase11_promotion_evidence_text


def _bundle(**overrides):
    shadow = {
        "target_field": "内科学",
        "learning_intent": "repair",
        "reason_code": "confident_wrong_cluster",
        "confidence": "high",
        "evidence": ["active_cross_question_confident_wrong_nodes=1"],
        "observations": ["high_same_day_volume"],
        "comparison": {
            "current_target": "小児学",
            "label": "different_target_shadow_has_stronger_evidence",
            "shadow_reason_profile_consistent": True,
            "current_target_formal_evidence": {
                "field_name": "小児学",
                "strongest_reason_code": "insufficient_coverage",
                "reason_rank": 5,
                "critical_safety_unresolved_count": 0,
                "answered_count": 4,
                "accuracy_percent": 100.0,
                "node_coverage_percent": 3.0,
            },
            "shadow_target_formal_evidence": {
                "field_name": "内科学",
                "strongest_reason_code": "confident_wrong_cluster",
                "reason_rank": 2,
                "active_cross_question_confident_wrong_node_count": 1,
                "active_confident_wrong_repairing_node_count": 2,
                "active_cross_question_wrong_node_count": 1,
                "active_repeated_weakness_node_count": 1,
                "critical_safety_unresolved_count": 0,
                "answered_count": 24,
                "accuracy_percent": 66.7,
                "node_coverage_percent": 18.0,
            },
        },
    }
    repeat = {
        "total_attempts": 30,
        "unique_questions": 30,
        "same_question_repeats": 2,
        "category_counts": {
            "justified_cooldown_bypass": 1,
            "adaptive_spaced_repeat": 1,
            "adaptive_unexplained_repeat": 0,
            "adaptive_metadata_inconsistent": 0,
            "nonadaptive_repeat": 0,
            "audit_metadata_unavailable": 0,
        },
    }
    saved = {
        "exists": True,
        "session_status": "complete",
        "event_count": 6,
        "question_count": 30,
        "unique_question_count": 30,
        "audit_fields_complete": True,
        "recent_repeat_count": 1,
        "cooldown_bypass_count": 1,
        "recent_repeat_question_ids": ["Q8"],
        "cooldown_bypass_question_ids": ["Q8"],
    }
    replay = {
        "plan_anchor_count": 2,
        "eligible_snapshot_count": 1,
        "coverage_excluded_count": 1,
        "agreement_count": 0,
        "shadow_stronger_disagreement_count": 1,
        "current_stronger_disagreement_count": 0,
        "inconclusive_disagreement_count": 0,
        "phase11_critical_safety_miss_candidate_count": 0,
        "baseline_stronger_safety_miss_candidate_count": 1,
        "ordinary_single_wrong_takeover_candidate_count": 0,
        "snapshots": [
            {
                "snapshot_jst": "2026-09-01T20:00:00+09:00",
                "eligible": True,
                "coverage_status": "history_coverage_complete",
                "coverage_issues": [],
                "baseline_target": "小児学",
                "baseline_goal": 10,
                "baseline_phase": "analysis",
                "shadow_target": "内科学",
                "shadow_reason_code": "confident_wrong_cluster",
                "comparison_label": "different_target_shadow_has_stronger_evidence",
                "review_category": "shadow_stronger_disagreement",
                "shadow_reason_profile_consistent": True,
                "phase11_critical_safety_miss_candidate": False,
                "baseline_stronger_safety_miss_candidate": False,
                "ordinary_single_wrong_takeover_candidate": False,
            },
            {
                "snapshot_jst": "2026-08-30T20:00:00+09:00",
                "eligible": False,
                "coverage_status": "history_coverage_incomplete",
                "coverage_issues": ["missing_attempt:event:1"],
                "baseline_target": "解剖学",
                "baseline_goal": 10,
                "baseline_phase": "foundation",
            },
        ],
    }
    kwargs = dict(
        period="7",
        shadow_judgment=shadow,
        repeat_structure_audit=repeat,
        saved_adaptive_daily_audit=saved,
        retrospective_shadow_audit=replay,
        state_counts={
            "unseen": 1000,
            "checking": 200,
            "repairing": 100,
            "repaired": 10,
            "recheck_due": 5,
            "stable": 20,
        },
        transitions={
            "repairing_to_repaired": 3,
            "repaired_to_repairing": 1,
            "recheck_due_to_stable": 2,
            "recheck_due_to_repairing": 1,
        },
        repairing_node_repairability={
            "repairing_node_total": 100,
            "strong_available_count": 12,
            "weak_only_count": 8,
            "same_or_blocked_count": 80,
            "repairable_rate": 12.0,
        },
        adaptive_count=30,
        adaptive_unique_questions=30,
        adaptive_unique_nodes=30,
        adaptive_groups={"repair": 15, "checking": 10, "exploration": 5},
    )
    kwargs.update(overrides)
    return build_phase11_promotion_evidence_text(**kwargs)


def test_bundle_contains_current_repeat_saved_replay_and_all_snapshot_evidence():
    text = _bundle()
    assert text.startswith("PHASE11_PROMOTION_EVIDENCE_V1\n")
    assert "selected_period=直近7日" in text
    assert "baseline_target=小児学" in text
    assert "shadow_target=内科学" in text
    assert "shadow_reason=confident_wrong_cluster" in text
    assert "shadow_evidence=active_cross_question_confident_wrong_nodes=1" in text
    assert "shadow_observations=high_same_day_volume" in text
    assert "comparison_label=different_target_shadow_has_stronger_evidence" in text
    assert "shadow_profile_consistent=true" in text
    assert "repeat=attempts:30,unique_q:30,same_q:2" in text
    assert "unexplained_recent:0" in text
    assert "saved_adaptive=exists:true,status:complete,events:6,questions:30,unique_q:30" in text
    assert "recent_q:Q8,bypass_q:Q8" in text
    assert "retrospective=anchors:2,eligible:1,excluded:1" in text
    assert "phase11_safety_miss:0" in text
    assert "baseline_safety_miss:1" in text
    assert "j2_j3_trigger_mismatch:0" in text
    assert "replay_snapshot_1=at:2026-09-01T20:00:00+09:00,eligible:true" in text
    assert "comparison:different_target_shadow_has_stronger_evidence" in text
    assert "replay_snapshot_2=at:2026-08-30T20:00:00+09:00,eligible:false" in text
    assert "coverage_issues:missing_attempt:event:1" in text
    assert "states=unseen:1000,checking:200,repairing:100,repaired:10,recheck_due:5,stable:20" in text
    assert "transitions=repairing_to_repaired:3,repaired_to_repairing:1,recheck_due_to_stable:2,recheck_due_to_repairing:1" in text
    assert "repairability=repairing_nodes:100,strong_available:12,weak_only:8,blocked:80,repairable_rate:12.0" in text
    assert "adaptive_simulation=count:30,unique_q:30,unique_nodes:30,repair:15,checking:10,exploration:5,maintenance:0" in text


def test_bundle_has_no_identity_token_or_consultation_fields_and_defaults_are_safe():
    text = _bundle(
        shadow_judgment={"reason_code": "maintenance_only", "comparison": {"shadow_reason_profile_consistent": True}},
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
    )
    lowered = text.lower()
    for forbidden in ("user_id", "learner_user_id", "supporter_token", "dashboard_token", "consultation", "相談内容"):
        assert forbidden not in lowered
    assert "shadow_target=none" in text
    assert "shadow_reason=maintenance_only" in text
    assert "saved_adaptive=exists:false,status:none" in text
    assert "retrospective=anchors:0,eligible:0,excluded:0" in text


def test_supporter_route_exposes_copy_button_but_learner_route_does_not(monkeypatch):
    diagnostics = {
        "period": "7",
        "promotion_evidence_text": "PHASE11_PROMOTION_EVIDENCE_V1\nselected_period=直近7日",
    }
    monkeypatch.setattr(goukaku_ui, "authorized_supporter_learner", lambda *_: ("supporter", "learner"))
    monkeypatch.setattr(goukaku_ui, "build_pilot_diagnostics", lambda *_: diagnostics)
    client = app.test_client()
    html = client.get("/supporter/pilot-diagnostics?token=test&period=7").get_data(as_text=True)
    assert "Phase11 Promotion evidenceをコピー" in html
    assert "PHASE11_PROMOTION_EVIDENCE_V1" in html
    assert "data-copy-q-ids=" in html
    learner_html = client.get("/goukaku-no-michi?token=invalid").get_data(as_text=True)
    assert "Phase11 Promotion evidenceをコピー" not in learner_html
