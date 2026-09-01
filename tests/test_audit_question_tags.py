from scripts.audit_question_tags import build_audit


def tag(qid, **overrides):
    item = {
        "id": qid,
        "tag_version": "1.0",
        "tag_status": "reviewed",
        "task": "fact_recall",
        "primary_ability": "KNOW",
        "secondary_ability": None,
        "level": 1,
        "safety": "none",
        "source": "past_exam",
    }
    item.update(overrides)
    return item


def test_build_audit_reports_clean_contiguous_bank_and_distributions():
    report = build_audit([
        tag("Q1"),
        tag("Q2", safety="critical", level=4, task="safety_priority", primary_ability="DECIDE"),
        tag("Q3", source="original"),
    ], expected_count=3)

    assert "records: 3" in report
    assert "Q range: Q1-Q3" in report
    assert "duplicates: 0" in report
    assert "missing: 0" in report
    assert "errors: 0" in report
    assert "safety:\n  critical: 1\n  none: 2" in report
    assert "source:\n  original: 1\n  past_exam: 2" in report


def test_build_audit_exposes_missing_duplicate_and_expected_count_errors():
    report = build_audit([tag("Q1"), tag("Q1"), tag("Q3")], expected_count=4)

    assert "duplicates: 1" in report
    assert "duplicate_ids: Q1" in report
    assert "missing: 2" in report
    assert "missing_ids: Q2, Q4" in report
    assert "errors: 2" in report
    assert "record_count_expected_4_actual_3" in report
    assert "max_q_expected_Q4_actual_Q3" in report


def test_build_audit_handles_null_secondary_ability():
    report = build_audit([tag("Q1")], expected_count=1)
    assert "secondary_ability:\n  null: 1" in report
