"""Fail-closed Lot04 validator configured from the reviewed Lot02 validation engine."""
from __future__ import annotations

import copy
import json
from pathlib import Path

from reports import question_bank_2000_lot02_validate as base

ROOT = Path(__file__).resolve().parents[1]
BANK = ROOT / "data" / "question_bank"
ROSTER = ROOT / "reports" / "question_bank_2000_lot04_targets_v01.json"
STAGING = ROOT / "staging" / "question_bank_2000_lot04_v01.json"
PROTECTED = base.PROTECTED
CATEGORY_QUOTA = {1:4,2:5,3:2,4:2,5:2,6:3,7:3,8:6,9:2,10:2,11:3,12:2,13:3,14:2,15:4,17:1,18:2}
TASK_QUOTA = {
    "assessment_selection":9,
    "device_selection":2,
    "fact_recall":2,
    "finding_interpretation":14,
    "functional_goal_decision":4,
    "intervention_selection":8,
    "prognosis_prediction":3,
    "safety_priority":6,
}
LEVEL_QUOTA = {1:2,2:16,3:20,4:10}
SLOT_QUOTA = {"singleton_second":27,"multi_reinforcement":17,"new_node":4}
SAFETY_AUGMENT = 12
MIN_STRONG = 37
BASE_COUNT = 1905
BASE_VERSION = "2026-09-b17"
INTEGRATED_START = 1906
INTEGRATED_END = 1953
INTEGRATED_VERSION = "2026-09-b18"

base.ROSTER = ROSTER
base.STAGING = STAGING
base.CATEGORY_QUOTA = CATEGORY_QUOTA
base.TASK_QUOTA = TASK_QUOTA
base.LEVEL_QUOTA = LEVEL_QUOTA
base.SLOT_QUOTA = SLOT_QUOTA
base.SAFETY_AUGMENT = SAFETY_AUGMENT
base.MIN_STRONG = MIN_STRONG
base.BASE_COUNT = BASE_COUNT
base.BASE_VERSION = BASE_VERSION
base.INTEGRATED_START = INTEGRATED_START
base.INTEGRATED_END = INTEGRATED_END
base.INTEGRATED_VERSION = INTEGRATED_VERSION

file_fingerprint = base.file_fingerprint
draft_fingerprint = base.draft_fingerprint


def build_report(payload: dict | None = None, *, require_seals: bool = True) -> dict:
    source = json.loads(STAGING.read_text(encoding="utf-8-sig")) if payload is None else payload
    normalized = copy.deepcopy(source)
    normalized["batch"] = "question_bank_2000_production_lot02_v01"
    return base.build_report(normalized, require_seals=require_seals)


def main() -> int:
    report = build_report()
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if report["hard_errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
