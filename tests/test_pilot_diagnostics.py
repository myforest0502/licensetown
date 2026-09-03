import os
from collections import Counter
from datetime import datetime, timedelta, timezone
os.environ.setdefault("OPENAI_API_KEY", "x")
os.environ.setdefault("CHANNEL_ACCESS_TOKEN", "x")
os.environ.setdefault("CHANNEL_SECRET", "x")

import database
import pilot_diagnostics
from app import app
from database import set_supporter_link
from goukaku_ui import create_supporter_token
from pilot_diagnostics import build_adaptive_selection_audit, build_pilot_diagnostics

NOW = datetime(2026, 8, 30, tzinfo=timezone.utc)

def attempt(q, days, correct, confidence, user="learner", selected=None):
    return {"event_key": f"{user}-{q}-{days}", "user_id": user, "question_id": q,
            "knowledge_node_id": f"KN{int(q[1:]):04d}", "mode": "study",
            "selected_answers": (["A"] if selected is None else selected), "is_correct": correct,
            "confidence": confidence, "answered_at": NOW-timedelta(days=days), "attempt_position": 1}

def setup_function():
    database._local_question_attempts.clear(); database._local_supporter_links.clear()

def test_period_behavior_confidence_unknown_and_user_isolation():
    database._local_question_attempts.extend([
        attempt("Q1",0,True,1), attempt("Q2",2,False,1), attempt("Q3",6,False,None,selected=[]),
        attempt("Q4",20,False,2), attempt("Q5",40,False,3), attempt("Q6",0,False,1,user="other")])
    seven=build_pilot_diagnostics("learner","7",NOW); thirty=build_pilot_diagnostics("learner","30",NOW); all_=build_pilot_diagnostics("learner","all",NOW)
    assert (seven["total_attempts"],thirty["total_attempts"],all_["total_attempts"]) == (3,4,5)
    assert seven["unique_questions"] == 3 and seven["correct"] == 1 and seven["incorrect"] == 2
    assert seven["confidence"] == {"1":2,"2":0,"3":0}
    assert seven["unknown"] == 1 and seven["confident_wrong"] == 1
    assert seven["touched_nodes"] == 5
    assert sum(seven["state_counts"].values()) == seven["canonical_node_total"]
    assert seven["adaptive_count"] == seven["adaptive_unique_questions"] == 30
    assert [item["question_id"] for item in seven["adaptive_details"]]
    assert Counter(item["priority_group"] for item in seven["adaptive_details"]) == Counter(seven["adaptive_groups"])

def test_diagnostics_route_requires_internal_admin_and_not_on_personal_dashboard(monkeypatch):
    set_supporter_link("supporter","learner")
    supporter_token=create_supporter_token("supporter")
    monkeypatch.setenv("LT_INTERNAL_ADMIN_TOKEN", "admin-secret")
    client=app.test_client()
    assert client.get("/internal/pilot-diagnostics?learner_user_id=learner").status_code == 403
    assert client.get("/internal/pilot-diagnostics?token=wrong&learner_user_id=learner").status_code == 403
    assert client.get(f"/supporter/pilot-diagnostics?token={supporter_token}&learner_user_id=learner").status_code == 404
    path="/internal/pilot-diagnostics?token=admin-secret&learner_user_id=learner&period=7"
    response=client.get(path); assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "LT学習診断" in html
    assert html.index("全期間") < html.index("直近7日") < html.index("直近30日")
    assert 'class="pilot-period-tab active" aria-current="page"' in html
    for label in ("学習範囲", "理解状態", "修復・定着", "最新のおすすめ30問シミュレーション", "分野横断の弱点候補"):
        assert label in html
    assert "30問の選定理由を見る" in html
    assert "30問監査データをコピー" in html
    assert html.count('class="adaptive-audit-item"') == 30
    assert "LT学習診断" not in client.get(f"/goukaku-no-michi?token=invalid").get_data(as_text=True)


def test_state_and_repair_retention_counts_use_pure_replay(monkeypatch):
    history = [attempt("Q1", 0, False, 2)]
    monkeypatch.setattr(pilot_diagnostics, "get_question_attempts", lambda user_id, start_at=None: history)
    monkeypatch.setattr(
        pilot_diagnostics,
        "derive_all_user_node_states",
        lambda attempts, as_of=None: [
            {"state": "checking"}, {"state": "repairing"}, {"state": "repaired"},
            {"state": "recheck_due"}, {"state": "stable"},
        ],
    )
    monkeypatch.setattr(
        pilot_diagnostics,
        "derive_state_timeline",
        lambda attempts: [
            {"state": "repairing"}, {"state": "repaired"},
            {"state": "repairing"}, {"state": "recheck_due"},
            {"state": "stable"}, {"state": "recheck_due"},
            {"state": "repairing"},
        ],
    )
    result = build_pilot_diagnostics("learner", "all", NOW)
    assert result["state_counts"]["checking"] == 1
    assert result["state_counts"]["repairing"] == 1
    assert result["state_counts"]["repaired"] == 1
    assert result["state_counts"]["recheck_due"] == 1
    assert result["state_counts"]["stable"] == 1
    assert result["repair_to_repaired"] == 1
    assert result["repaired_to_repairing"] == 1
    assert result["due_to_stable"] == 1
    assert result["due_to_repairing"] == 1


def test_adaptive_audit_preserves_selector_order_and_uses_formal_node_label():
    selected = [
        {
            "question_id": "Q1", "canonical_node_id": "KN0001", "state": "repairing",
            "priority_group": "repair", "priority_reason": "confident_wrong",
            "priority_score": 950, "strong_repair_confirmation": True,
            "same_question_repeat": False,
        },
        {
            "question_id": "Q2", "canonical_node_id": "KN0002", "state": "unseen",
            "priority_group": "exploration", "priority_reason": "unseen",
            "priority_score": 310, "strong_repair_confirmation": False,
            "same_question_repeat": False,
        },
    ]
    original = [dict(item) for item in selected]
    details, audit_text = build_adaptive_selection_audit(selected)
    assert selected == original
    assert [item["question_id"] for item in details] == ["Q1", "Q2"]
    assert [item["rank"] for item in details] == [1, 2]
    assert details[0]["node_label"] != "名称未登録"
    assert details[0]["state_label"] == "修復中"
    assert details[0]["group_label"] == "修復"
    assert "自信あり誤答" in details[0]["reason_label"]
    assert "strong別問題の修復確認候補" in details[0]["reason_label"]
    assert "1. Q1 / KN0001" in audit_text and "2. Q2 / KN0002" in audit_text
