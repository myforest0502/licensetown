from reports.question_bank_2000_batch01_validate import build_report


def test_batch01_staging_matches_current_formal_bank():
    report = build_report()
    assert report["accepted_count"] == 12
    assert report["hard_errors"] == [], "\n" + "\n".join(report["hard_errors"])


def test_batch01_changes_task_or_primary_ability_from_reference():
    report = build_report()
    same_demand = [
        row["draft_id"]
        for row in report["rows"]
        if row["draft_task"] == row["reference_task"]
        and row["draft_primary_ability"] == row["reference_primary_ability"]
    ]
    assert same_demand == [], (
        "Metadata-level same-demand candidates need content review before STRONG intent: "
        + ", ".join(same_demand)
    )
