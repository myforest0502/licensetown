"""Build the structural authoring template for Question Bank 2000 production Lot 01."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGETS = ROOT / "reports" / "question_bank_2000_lot01_targets_v01.json"
OUT = ROOT / "staging" / "question_bank_2000_lot01_template_v01.json"
TASK_QUOTA = {
    "assessment_selection":9,
    "device_selection":2,
    "fact_recall":1,
    "finding_interpretation":14,
    "functional_goal_decision":4,
    "intervention_selection":9,
    "prognosis_prediction":3,
    "safety_priority":6,
}
LEVEL_QUOTA = {"1":1,"2":16,"3":20,"4":11}
CATEGORY_QUOTA = {"9":12,"16":10,"17":12,"18":14}


def blank_content() -> dict:
    return {
        "title": "",
        "question_text": "",
        "choices": {"1":"","2":"","3":"","4":"","5":""},
        "correct_choices": [],
        "explanation": "",
        "choice_explanations": {"1":"","2":"","3":"","4":"","5":""},
        "proposed_task": "",
        "primary_ability": "",
        "secondary_ability": None,
        "level": None,
        "safety": "none",
        "clinical_intent": "",
        "semantic_review": {
            "reference_demand": "",
            "candidate_demand": "",
            "why_not_same_demand": "",
            "related_formal_questions": [],
            "decision": "pending",
            "reviewer": "",
            "reviewed_on": "",
            "expert_signoff": False,
        },
        "evidence": [],
        "reviewed_sha256": "",
    }


def main() -> int:
    roster = json.loads(TARGETS.read_text(encoding="utf-8"))
    drafts = []
    for target in roster["existing_node_targets"]:
        item = {
            "draft_id": target["lot_target_id"],
            "status": "authoring",
            "slot_type": target["slot_type"],
            "target_node_id": target["canonical_node_id"],
            "target_node_label": target["label"],
            "reference_question_ids": target["question_ids"],
            "existing_demands": target["existing_demands"],
            "proposed_category_small": target["category_small"],
            "source": "original",
            "required_new_demand_outside_existing": True,
            **blank_content(),
        }
        drafts.append(item)
    for reservation in roster["new_node_reservations"]:
        category = int(reservation["category_small"])
        item = {
            "draft_id": f"L01-C{category}-N01",
            "status": "authoring",
            "slot_type": "new_node",
            "target_node_id": None,
            "target_node_label": "",
            "reference_question_ids": [],
            "existing_demands": [],
            "proposed_category_small": category,
            "source": "original",
            "required_new_demand_outside_existing": False,
            "new_node_created_only_at_formal_integration": True,
            **blank_content(),
        }
        drafts.append(item)
    if len(drafts) != 48 or len({d["draft_id"] for d in drafts}) != 48:
        raise ValueError("Lot01 authoring template must contain 48 unique drafts")
    payload = {
        "batch": "question_bank_2000_production_lot01_v01",
        "status": "template_only",
        "formal_baseline": "Q1-Q1761",
        "q_ids_reserved": False,
        "production_write": False,
        "db_write": False,
        "accepted_target_count": 48,
        "quotas": {
            "category": CATEGORY_QUOTA,
            "task": TASK_QUOTA,
            "level": LEVEL_QUOTA,
            "slot_type": {"singleton_second":32,"multi_reinforcement":12,"new_node":4},
            "minimum_strong_formations":41,
            "safety_moderate_or_critical":12,
        },
        "drafts": drafts,
        "authoring_rules": [
            "Do not allocate formal Q IDs in staging.",
            "Each existing-Node draft must add a genuinely different semantic demand, not only a changed metadata label.",
            "All five choices and all five choice explanations are required; single-best answer by default.",
            "Stem <=300 Japanese characters unless a clinically necessary exception is documented and <=400.",
            "New-Node slots require semantic search against the formal bank before a Node label is proposed.",
            "Every accepted draft requires evidence URLs/support and a completed semantic_review before sealing.",
        ],
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"drafts":len(drafts),"existing":44,"new_node":4,"output":str(OUT.relative_to(ROOT))},ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
