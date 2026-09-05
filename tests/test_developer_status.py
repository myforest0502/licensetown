import developer_status


def test_formal_bank_status_matches_frozen_b12_data():
    status = developer_status.build_developer_system_status()
    bank = status["question_bank"]
    assert bank["version"] == "2026-09-b12"
    assert bank["question_count"] == 1737
    assert bank["first_question_number"] == 1
    assert bank["last_question_number"] == 1737
    assert bank["records"] == 1737
    assert bank["errors"] == 0
    assert bank["status"] == "PASS"
    assert bank["original"] == 643
    assert bank["past_exam"] == 1094


def test_status_reports_knowledge_node_and_safety_counts():
    bank = developer_status.build_developer_system_status()["question_bank"]
    assert bank["canonical_registry"] == 1538
    assert bank["canonical_represented"] == 1508
    assert bank["canonical_singleton"] == 1305
    assert bank["canonical_multi"] == 203
    assert bank["shared_groups"] == 186
    assert bank["safety_critical"] == 65
    assert bank["safety_moderate"] == 232


def test_feature_flags_are_boolean_and_do_not_expose_values(monkeypatch):
    monkeypatch.setenv("LT_LEARNER_PATH_PERF_LOG", "true")
    monkeypatch.setenv("LT_SUPPORTER_PERF_LOG", "false")
    flags = developer_status.build_developer_system_status()["feature_flags"]
    assert flags["learner_perf_log"] is True
    assert flags["supporter_perf_log"] is False
    assert all(isinstance(value, bool) for value in flags.values())
