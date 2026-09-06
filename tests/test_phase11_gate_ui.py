import os
from pathlib import Path

os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ.setdefault("CHANNEL_ACCESS_TOKEN", "test-token")
os.environ.setdefault("CHANNEL_SECRET", "test-secret")

from flask import Flask

import phase11_gate_ui


ROOT = Path(__file__).resolve().parents[1]


def _app():
    app = Flask(
        "phase11-gate-ui-test",
        template_folder=str(ROOT / "templates"),
    )
    phase11_gate_ui.install_phase11_gate_ui(app)
    return app


def test_gate_page_requires_internal_admin_token(monkeypatch):
    monkeypatch.setenv("LT_INTERNAL_ADMIN_TOKEN", "admin-secret")
    client = _app().test_client()
    assert client.get("/internal/phase11-gates?learner_user_id=learner").status_code == 403
    assert client.get("/internal/phase11-gates?token=wrong&learner_user_id=learner").status_code == 403


def test_gate_page_renders_hold_retention_and_no_auto_promotion(monkeypatch):
    monkeypatch.setenv("LT_INTERNAL_ADMIN_TOKEN", "admin-secret")
    monkeypatch.setattr(
        phase11_gate_ui,
        "build_phase11_gate_dashboard",
        lambda learner_id, period: {
            "period": period,
            "diagnostics": {
                "state_counts": {"checking": 2, "repairing": 3, "repaired": 1, "recheck_due": 0, "stable": 0},
                "due_to_stable": 0,
                "due_to_repairing": 0,
            },
            "session_load": {
                "answered_count": 200,
                "accuracy_percent": 74.5,
                "unique_question_count": 148,
                "repeat_attempt_count": 52,
                "first_attempt_accuracy_percent": 70.3,
                "repeat_accuracy_percent": 86.5,
                "repeat_after_wrong_accuracy_percent": 54.5,
                "max_inter_attempt_gap_minutes": 322.0,
                "leading_to_trailing_full_block_accuracy_delta_pp": -10.0,
            },
            "repair_effectiveness": {
                "adaptive_repair_attempt_count": 45,
                "strong_attempt_count": 35,
                "strong_correct_count": 26,
                "strong_accuracy_percent": 74.3,
                "formal_confirmation_candidate_count": 13,
                "strong_wrong_count": 9,
                "strong_recent_repeat_count": 0,
                "strong_cooldown_bypass_count": 0,
            },
            "retention_horizon": {
                "recheck_due_count": 0,
                "due_within_24h_count": 0,
                "due_within_3d_count": 4,
                "due_within_7d_count": 13,
                "upcoming_review_count": 13,
                "earliest_review_at_jst": "2026-09-09T08:26:32+09:00",
                "earliest_review_in_hours": 63.4,
            },
            "retention_supply": {
                "due_node_count": 0,
                "due_strong_available_count": 0,
                "due_without_strong_count": 0,
                "upcoming_repaired_node_count": 13,
                "upcoming_without_strong_count": 2,
                "weak_only_count": 1,
                "no_formal_alternate_count": 1,
            },
            "retention_outcomes": {
                "review_attempt_count": 0,
                "stable_count": 0,
                "repairing_count": 0,
                "still_due_count": 0,
                "strong_evidence_count": 0,
                "weak_evidence_count": 0,
                "same_question_count": 0,
                "confident_correct_count": 0,
            },
            "gate_status": {
                "decision": "hold",
                "blocked_gates": [],
                "open_gates": ["retention", "comparison_diversity"],
                "gates": {
                    "safety": {"status": "pass"},
                    "repeat_audit": {"status": "pass"},
                    "formal_trigger_consistency": {"status": "pass"},
                    "retention": {"status": "open"},
                    "comparison_diversity": {"status": "open"},
                    "profile_consistency": {"status": "pass"},
                },
            },
        },
    )
    response = _app().test_client().get(
        "/internal/phase11-gates?token=admin-secret&learner_user_id=learner&period=7"
    )
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Phase11 Gate Status" in html
    assert "HOLD" in html
    assert "Retention Horizon" in html
    assert "Retention STRONG Supply Preflight" in html
    assert "upcomingでSTRONGなし 2" in html
    assert "Natural Retention Outcomes" in html
    assert "自然なretention review 0" in html
    assert "2026-09-09T08:26:32+09:00" in html
    assert "自動昇格なし" in html
    assert "learner-facing promotion allowed = false" in html
    assert "誤答後repeat正答率 54.5%" in html
    assert "STRONG＋自信あり正解候補 13" in html
    assert "admin-secret" not in html


def test_install_is_idempotent():
    app = _app()
    rules_before = len(list(app.url_map.iter_rules()))
    phase11_gate_ui.install_phase11_gate_ui(app)
    assert len(list(app.url_map.iter_rules())) == rules_before
