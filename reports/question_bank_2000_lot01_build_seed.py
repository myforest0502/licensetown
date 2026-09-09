"""Build a non-final Lot01 authoring seed by combining template and quota-exact suggestions."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "staging" / "question_bank_2000_lot01_template_v01.json"
ASSIGNMENT = ROOT / "reports" / "question_bank_2000_lot01_assignment_v01.json"
OUT = ROOT / "staging" / "question_bank_2000_lot01_authoring_seed_v01.json"


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def main() -> int:
    template = read(TEMPLATE)
    assignment = read(ASSIGNMENT)
    by_id = {row["draft_id"]: row for row in assignment["assignments"]}
    drafts = []
    for original in template["drafts"]:
        draft = json.loads(json.dumps(original, ensure_ascii=False))
        suggestion = by_id[draft["draft_id"]]
        draft["proposed_task"] = suggestion["suggested_task"]
        draft["primary_ability"] = suggestion["suggested_primary_ability"]
        draft["level"] = suggestion["suggested_level"]
        draft["safety"] = suggestion["suggested_safety"]
        draft["assignment_status"] = "suggested_not_editorially_approved"
        draft["assignment_may_change_if_quotas_preserved"] = True
        draft["semantic_review"]["candidate_demand"] = (
            f"suggested {suggestion['suggested_task']} / {suggestion['suggested_primary_ability']}"
        )
        if not suggestion["is_new"]:
            existing = ", ".join(
                f"{x['task']}/{x['primary_ability']}" for x in suggestion["existing_demands"]
            )
            draft["semantic_review"]["reference_demand"] = f"existing demands: {existing}"
        drafts.append(draft)

    output = {
        **{k:v for k,v in template.items() if k != "drafts"},
        "batch":"question_bank_2000_production_lot01_v01",
        "status":"authoring_seed_only",
        "drafts":drafts,
        "seed_warning":"Suggested task/level/Safety values are quota-exact structural aids only. Medical authoring may change them if the final validator quotas remain exact.",
    }
    if len(drafts) != 48 or len({d["draft_id"] for d in drafts}) != 48:
        raise ValueError("authoring seed must contain 48 unique drafts")
    OUT.write_text(json.dumps(output,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"output":str(OUT.relative_to(ROOT)),"drafts":48},ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
