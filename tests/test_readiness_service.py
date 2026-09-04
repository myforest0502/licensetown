from __future__ import annotations

import readiness_service


def test_readiness_service_passes_trial100_records_to_evaluator(monkeypatch):
    attempts = [{"user_id": "learner", "question_id": "Q1"}]
    evidence = {"fields": [], "canonical_node_evidence": []}
    progress = {
        "overall": {
            "total_unique_canonical_nodes": 1,
            "touched_unique_canonical_nodes": 0,
            "state_counts": {},
        }
    }
    trial100 = [
        {"user_id": "learner", "timed_full_format": True, "supportive": False}
    ]
    captured = {}

    monkeypatch.setattr(readiness_service, "get_question_attempts", lambda user_id: attempts)
    monkeypatch.setattr(readiness_service, "build_field_evidence", lambda rows: evidence)
    monkeypatch.setattr(readiness_service, "build_field_progress", lambda rows: progress)
    monkeypatch.setattr(readiness_service, "get_trial100_records", lambda user_id: trial100)

    def fake_build(rows, field_evidence=None, progress=None, trial100_records=None):
        captured.update(
            rows=rows,
            field_evidence=field_evidence,
            progress=progress,
            trial100_records=trial100_records,
        )
        return {"status": "building_coverage"}

    monkeypatch.setattr(readiness_service, "build_pass_readiness", fake_build)

    result = readiness_service.build_pass_readiness_for_user("learner")

    assert result == {"status": "building_coverage"}
    assert captured["rows"] == attempts
    assert captured["field_evidence"] is evidence
    assert captured["progress"] is progress
    assert captured["trial100_records"] == trial100


def test_readiness_service_rejects_blank_user_id():
    try:
        readiness_service.build_pass_readiness_for_user("  ")
    except ValueError as exc:
        assert str(exc) == "user_id is required"
    else:
        raise AssertionError("blank user_id must be rejected")
