from reports.question_bank_2000_batch01_validate import build_report


def test_batch01_staging_matches_current_formal_bank():
    report = build_report()
    assert report["accepted_count"] == 12
    assert report["hard_errors"] == [], "\n" + "\n".join(report["hard_errors"])
