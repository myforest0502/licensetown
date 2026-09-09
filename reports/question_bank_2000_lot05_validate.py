"""Fail-closed Lot05 validator configured from the proven Lot02 validation engine."""
from __future__ import annotations
import copy,json
from pathlib import Path
from reports import question_bank_2000_lot02_validate as base
ROOT=Path(__file__).resolve().parents[1]
BANK=ROOT/'data'/'question_bank'
ROSTER=ROOT/'reports'/'question_bank_2000_lot05_targets_reviewed_v01.json'
STAGING=ROOT/'staging'/'question_bank_2000_lot05_v01.json'
PROTECTED=base.PROTECTED
CATEGORY_QUOTA={1:4,2:5,3:1,4:2,5:1,6:2,7:3,8:5,9:1,10:2,11:2,12:1,13:3,14:2,15:3,17:2,18:2}
TASK_QUOTA={'assessment_selection':7,'device_selection':1,'fact_recall':1,'finding_interpretation':13,'functional_goal_decision':4,'intervention_selection':7,'prognosis_prediction':3,'safety_priority':5}
LEVEL_QUOTA={1:1,2:13,3:18,4:9}
SLOT_QUOTA={'singleton_second':18,'multi_reinforcement':20,'new_node':3}
SAFETY_AUGMENT=11
MIN_STRONG=26
ACCEPTED_COUNT=41
BASE_COUNT=1953
BASE_VERSION='2026-09-b18'
INTEGRATED_START=1954
INTEGRATED_END=1994
INTEGRATED_VERSION='2026-09-b19'
base.ROSTER=ROSTER;base.STAGING=STAGING;base.CATEGORY_QUOTA=CATEGORY_QUOTA;base.TASK_QUOTA=TASK_QUOTA;base.LEVEL_QUOTA=LEVEL_QUOTA;base.SLOT_QUOTA=SLOT_QUOTA;base.SAFETY_AUGMENT=SAFETY_AUGMENT;base.MIN_STRONG=MIN_STRONG;base.ACCEPTED_COUNT=ACCEPTED_COUNT;base.BASE_COUNT=BASE_COUNT;base.BASE_VERSION=BASE_VERSION;base.INTEGRATED_START=INTEGRATED_START;base.INTEGRATED_END=INTEGRATED_END;base.INTEGRATED_VERSION=INTEGRATED_VERSION
file_fingerprint=base.file_fingerprint
draft_fingerprint=base.draft_fingerprint
def build_report(payload=None,*,require_seals=True):
    source=json.loads(STAGING.read_text(encoding='utf-8-sig')) if payload is None else payload
    normalized=copy.deepcopy(source); normalized['batch']='question_bank_2000_production_lot02_v01'
    return base.build_report(normalized,require_seals=require_seals)
def main():
    report=build_report(); print(json.dumps(report,ensure_ascii=False,indent=2)); return 1 if report['hard_errors'] else 0
if __name__=='__main__': raise SystemExit(main())
