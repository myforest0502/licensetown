import json

import developer_status


def test_formal_bank_status_matches_manifest_and_saved_audit():
    status = developer_status.build_developer_system_status()
    bank = status["question_bank"]
    manifest = json.loads(developer_status.MANIFEST_PATH.read_text(encoding="utf-8-sig"))
    assert bank["version"] == manifest["bank_version"]
    assert bank["question_count"] == manifest["question_count"]
    assert bank["first_question_number"] == manifest["first_question_number"]
    assert bank["last_question_number"] == manifest["last_question_number"]
    # Audit fields are the saved formal-bank audit, regenerated at integration.
    assert bank["records"] == 1905
    assert bank["errors"] == 0
    assert bank["status"] == "PASS"
    assert bank["original"] == 811
    assert bank["past_exam"] == 1094


def test_status_reports_knowledge_node_and_safety_counts():
    bank = developer_status.build_developer_system_status()["question_bank"]
    assert bank["canonical_registry"] == 1551
    assert bank["canonical_represented"] == 1521
    assert bank["canonical_singleton"] == 1201
    assert bank["canonical_multi"] == 320
    assert bank["shared_groups"] == 312
    assert bank["safety_critical"] == 91
    assert bank["safety_moderate"] == 262


def test_feature_flags_are_boolean_and_do_not_expose_values(monkeypatch):
    monkeypatch.setenv("LT_LEARNER_PATH_PERF_LOG", "true")
    monkeypatch.setenv("LT_SUPPORTER_PERF_LOG", "false")
    flags = developer_status.build_developer_system_status()["feature_flags"]
    assert flags["learner_perf_log"] is True
    assert flags["supporter_perf_log"] is False
    assert all(isinstance(value, bool) for value in flags.values())
