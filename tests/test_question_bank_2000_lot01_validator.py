import copy
import json
from pathlib import Path

from reports.question_bank_2000_lot01_validate import (
    STAGING,
    build_report,
    draft_fingerprint,
)


ROOT = Path(__file__).parents[1]
TEMPLATE = ROOT / "staging" / "question_bank_2000_lot01_template_v01.json"
ASSIGNMENT = ROOT / "reports" / "question_bank_2000_lot01_assignment_v01.json"


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def test_final_staging_is_not_silently_present_before_authoring():
    # PR #268 is infrastructure-only. A final authored staging file must be a
    # deliberate later artifact, never an alias/copy silently created by planning.
    assert not STAGING.exists()


def test_blank_template_cannot_be_mislabeled_as_accepted_and_pass_validator():
    payload = read(TEMPLATE)
    payload["batch"] = "question_bank_2000_production_lot01_v01"
    payload["status"] = "staging_only"
    for draft in payload["drafts"]:
        draft["status"] = "accepted"
    report = build_report(payload, require_seals=False)
    assert report["hard_errors"]
    text = "\n".join(report["hard_errors"])
    assert "question text required" in text
    assert "single best answer required" in text
    assert "medical evidence required" in text
    assert "semantic review not accepted" in text


def test_assignment_plan_is_quota_exact_and_every_existing_target_is_distinct():
    payload = read(ASSIGNMENT)
    assert payload["status"] == "authoring_suggestions_only"
    assert payload["task_counts"] == {
        "finding_interpretation": 14,
        "prognosis_prediction": 3,
        "safety_priority": 6,
        "assessment_selection": 9,
        "functional_goal_decision": 4,
        "intervention_selection": 9,
        "device_selection": 2,
        "fact_recall": 1,
    }
    assert payload["level_counts"] == {"2": 16, "4": 11, "3": 20, "1": 1}
    assert payload["safety_moderate_or_critical"] == 12
    assert payload["structurally_distinct_existing_assignments"] == 44
    for row in payload["assignments"]:
        if row["is_new"]:
            continue
        old = {(x["task"], x["primary_ability"]) for x in row["existing_demands"]}
        assert (row["suggested_task"], row["suggested_primary_ability"]) not in old


def test_review_seal_changes_when_editorial_content_changes():
    template = read(TEMPLATE)
    draft = copy.deepcopy(template["drafts"][0])
    draft["status"] = "accepted"
    draft["question_text"] = "仮の問題文"
    first = draft_fingerprint(draft)
    draft["question_text"] = "変更された仮の問題文"
    second = draft_fingerprint(draft)
    assert first != second
