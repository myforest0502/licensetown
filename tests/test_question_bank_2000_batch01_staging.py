from reports.question_bank_2000_batch01_validate import build_report


def test_batch01_staging_matches_current_formal_bank():
    report = build_report()
    assert report["accepted_count"] == 12
    assert report["hard_errors"] == [], "\n" + "\n".join(report["hard_errors"])


def test_batch01_changes_task_or_primary_ability_from_reference():
    report = build_report()
    same_demand = [
        row
        for row in report["rows"]
        if row["draft_task"] == row["reference_task"]
        and row["draft_primary_ability"] == row["reference_primary_ability"]
    ]
    details = "\n\n".join(
        f"{row['draft_id']} / {row['reference_qid']} / "
        f"{row['reference_task']} / {row['reference_primary_ability']}\n"
        f"REF: {row['reference_question_text']}\n"
        f"NEW: {row['draft_question_text']}"
        for row in same_demand
    )
    assert same_demand == [], (
        "Metadata-level same-demand candidates need semantic review before STRONG intent:\n"
        + details
    )
