import copy
from datetime import datetime, timedelta, timezone
import os

os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ.setdefault("CHANNEL_ACCESS_TOKEN", "test-token")
os.environ.setdefault("CHANNEL_SECRET", "test-secret")

from app import app
import developer_ui
import pilot_diagnostics
from pilot_diagnostics import build_confident_wrong_node_details


NOW = datetime(2026, 9, 1, 12, 0, tzinfo=timezone.utc)


def _attempt(node, question, *, confidence=1, unknown=False, days=0):
    return {
        "user_id": "learner",
        "knowledge_node_id": node,
        "question_id": question,
        "is_correct": False,
        "confidence": confidence,
        "answer_status": "unknown" if unknown else "answered",
        "selected_answers": [] if unknown else ["A"],
        "answered_at": NOW - timedelta(days=days),
        "event_key": f"{node}-{question}-{confidence}-{unknown}-{days}",
        "attempt_position": 1,
    }


def _evidence(nodes):
    return {
        "canonical_node_evidence": [
            {"canonical_node_id": node, "state": "repairing"}
            for node in nodes
        ]
    }


def test_five_target_field_nodes_are_exposed_without_changing_shadow(monkeypatch):
    nodes = [f"KN9{index:03d}" for index in range(1, 6)]
    field_by_question = {
        "Q101": 8, "Q102": 8, "Q103": 8, "Q104": 8, "Q105": 8,
        "Q106": 8, "Q200": 9, "Q201": 8, "Q202": 8,
    }
    monkeypatch.setattr(
        pilot_diagnostics,
        "get_category_small",
        lambda question_id: field_by_question[str(question_id)],
    )
    monkeypatch.setattr(
        pilot_diagnostics,
        "_NODE_LABELS",
        {node: f"内科学知識{index}" for index, node in enumerate(nodes, 1)},
    )
    attempts = [
        _attempt(nodes[0], "Q101", days=2),
        _attempt(nodes[0], "Q102", confidence=2, days=1),
        *[_attempt(node, f"Q{102 + index}") for index, node in enumerate(nodes[1:], 1)],
        _attempt("KN9998", "Q200"),
        _attempt("KN9997", "Q201", unknown=True),
        _attempt("KN9997", "Q202", confidence=2),
    ]
    shadow = {"reason_code": "confident_wrong_cluster", "target_field": "内科学"}
    shadow_before = copy.deepcopy(shadow)
    details = build_confident_wrong_node_details(
        attempts,
        _evidence(nodes + ["KN9997", "KN9998"]),
        shadow,
        as_of=NOW,
    )
    assert shadow == shadow_before
    assert len(details) == 5
    assert {item["canonical_node_id"] for item in details} == set(nodes)
    assert details[0]["question_ids"] == ["Q101", "Q102"]
    assert details[0]["cross_question"] is True
    assert all(item["confident_wrong_count"] == 1 for item in details)
    assert all(item["node_state"] == "repairing" for item in details)
    assert not any(item["canonical_node_id"] in {"KN9997", "KN9998"} for item in details)


def test_details_are_empty_for_other_shadow_reasons():
    assert build_confident_wrong_node_details(
        [_attempt("KN9001", "Q101")],
        _evidence(["KN9001"]),
        {"reason_code": "repeated_wrong_cluster", "target_field": "内科学"},
        as_of=NOW,
    ) == []


def test_internal_template_lists_all_details_but_learner_page_never_does(monkeypatch):
    details = [
        {
            "canonical_node_id": f"KN9{index:03d}",
            "knowledge_text": f"内科学知識{index}",
            "question_ids": [f"Q{100 + index}"],
            "confident_wrong_count": 1,
            "distinct_question_count": 1,
            "cross_question": index == 1,
            "node_state": "repairing",
            "node_state_label": "修復中",
            "last_wrong_at": "2026/09/01 20:00",
        }
        for index in range(1, 6)
    ]
    original = pilot_diagnostics.build_pilot_diagnostics
    diagnostics = original("learner", "all", NOW)
    diagnostics["shadow_judgment"].update({
        "reason_code": "confident_wrong_cluster",
        "target_field": "内科学",
    })
    diagnostics["confident_wrong_node_details"] = details
    monkeypatch.setenv("LT_INTERNAL_ADMIN_TOKEN", "admin-secret")
    monkeypatch.setattr(developer_ui, "build_pilot_diagnostics", lambda *_: diagnostics)
    client = app.test_client()
    html = client.get(
        "/internal/pilot-diagnostics?token=admin-secret&learner_user_id=learner&period=all"
    ).get_data(as_text=True)
    assert "自信あり誤答Node詳細" in html
    assert "対象 5 Node" in html
    assert html.count("内科学知識") == 5
    assert "Q101" in html
    assert "別問題証拠：</b>あり" in html
    learner_html = client.get("/goukaku-no-michi?token=invalid").get_data(as_text=True)
    assert "自信あり誤答Node詳細" not in learner_html
