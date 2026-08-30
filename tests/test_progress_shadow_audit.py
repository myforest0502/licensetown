from datetime import datetime, timedelta, timezone
import json
import sys

import progress_shadow_audit as audit
from field_evidence import build_field_evidence
from field_progress import build_field_progress
from question_bank import get_question_tag, question_ids


BASE = datetime(2026, 8, 30, tzinfo=timezone.utc)


def attempt(q, correct=True, confidence=1, minute=0, *, user="u"):
    return {
        "user_id": user, "question_id": q,
        "knowledge_node_id": get_question_tag(q)["knowledge_node_id"],
        "is_correct": correct, "confidence": confidence,
        "selected_answers": ["1"], "answer_status": "answered",
        "answered_at": BASE + timedelta(minutes=minute),
        "event_key": f"e-{user}-{minute}", "attempt_position": 1,
    }


def test_no_history_is_safe_and_returns_all_fields():
    report = audit.build_progress_shadow_audit(build_field_evidence([]))
    assert len(report["fields"]) == 18
    assert report["overall"]["total_unique_canonical_nodes"] == 1509
    assert report["overall"]["touched_unique_canonical_nodes"] == 0
    assert report["overall"]["overall_progress_score"] == 0
    assert report["legacy"]["overall_progress_percent"] is None
    assert report["overall"]["question_accuracy_percent"] is None


def test_low_history_keeps_raw_score_and_both_rounding_candidates():
    evidence = build_field_evidence([attempt("Q269")])
    report = audit.build_progress_shadow_audit(evidence, legacy={
        "overall_progress_percent": 4, "question_attempt_count": 1,
        "question_correct_count": 1,
    })
    overall = report["overall"]
    assert 0 < overall["overall_progress_score"] < 0.01
    assert overall["question_accuracy_percent"] == 100
    assert overall["rounding_candidates"]["raw_score"] == overall["overall_progress_score"]
    assert "integer_percent" in overall["rounding_candidates"]
    assert "one_decimal_percent" in overall["rounding_candidates"]
    assert report["legacy"]["overall_progress_percent"] == 4


def test_high_history_fixture_increases_coverage_and_progress():
    low = audit.build_progress_shadow_audit(build_field_evidence([attempt("Q1")]))
    ids = list(question_ids())[:200]
    high = audit.build_progress_shadow_audit(build_field_evidence([
        attempt(q, minute=index) for index, q in enumerate(ids)
    ]))
    assert high["overall"]["node_coverage"] > low["overall"]["node_coverage"]
    assert high["overall"]["overall_progress_score"] > low["overall"]["overall_progress_score"]


def test_rankings_gaps_and_progress_match_existing_calculation():
    evidence = build_field_evidence([
        attempt("Q269", True, minute=1),
        attempt("Q1", False, 2, minute=2),
    ])
    report = audit.build_progress_shadow_audit(evidence)
    direct = build_field_progress(evidence)
    assert len(report["fields"]) == 18
    assert report["overall"]["overall_progress_score"] == direct["overall"]["overall_progress_score"]
    assert len(report["rankings"]["field_progress_high"]) == 18
    assert len(report["rankings"]["node_coverage_low"]) == 18
    learned = [item for item in report["fields"] if item["field_answer_count"]]
    assert all(item["accuracy_progress_gap_points"] is not None for item in learned)


def test_multi_field_node_is_unique_overall():
    evidence = build_field_evidence([
        attempt("Q1225", False, 2, minute=1),
        attempt("Q1363", False, 2, minute=2),
    ])
    report = audit.build_progress_shadow_audit(evidence)
    assert report["overall"]["total_unique_canonical_nodes"] == 1509
    assert report["overall"]["touched_unique_canonical_nodes"] == 1
    assert report["multi_field_node_count"] == 14
    assert report["canonical_node_membership_total"] == 1525


def test_user_adapter_reads_one_user_and_never_returns_identifier(monkeypatch):
    calls = []
    monkeypatch.setattr(audit, "get_question_attempts", lambda user: calls.append(("attempts", user)) or [])
    monkeypatch.setattr(audit, "get_dashboard_learning_data", lambda user: calls.append(("dashboard", user)) or {
        "summary": {"study_minutes": 0, "total_answers": 0, "average_accuracy": 0},
        "unique_question_count": 0,
    })
    monkeypatch.setattr(audit, "calculate_overall_progress", lambda *_: 0)
    report = audit.get_user_progress_shadow_audit("secret-user")
    assert calls == [("attempts", "secret-user"), ("dashboard", "secret-user")]
    assert "secret-user" not in str(report)


def test_recheck_due_impact_is_explanatory_only():
    evidence = build_field_evidence([])
    node = evidence["canonical_node_evidence"][0]
    node["state"] = "recheck_due"
    field_id = node["field_ids"][0]
    field = next(x for x in evidence["fields"] if x["field_id"] == field_id)
    field["state_counts"]["unseen"] -= 1
    field["state_counts"]["recheck_due"] += 1
    field["unseen_node_count"] -= 1
    field["recheck_due_node_count"] += 1
    report = audit.build_progress_shadow_audit(evidence)
    impact = report["recheck_due_impact"]
    assert impact["recheck_due_node_count"] == 1
    assert impact["score_contribution"] == 0.6
    assert impact["difference_vs_repaired_score"] < 0
    assert not impact["score_changed_by_audit"]


def test_cli_without_database_is_safe(monkeypatch, capsys):
    from scripts import audit_production_field_progress as script
    monkeypatch.setattr(script, "database_is_available", lambda: False)
    monkeypatch.setattr(sys, "argv", ["audit_production_field_progress.py"])
    assert script.main() == 0
    result = json.loads(capsys.readouterr().out)
    assert not result["production_read_only_executed"]
    assert result["db_write_count"] == 0
