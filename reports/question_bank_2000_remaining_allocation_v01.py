"""Read-only recalculation of the remaining Question Bank 2000 allocation."""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BANK = ROOT / "data" / "question_bank"
BASE_END = 1737
CURRENT_END = 1761
FINAL_TARGET = 2000

CATEGORY_TARGET = {1:12,2:16,3:4,4:7,5:4,6:8,7:10,8:25,9:28,10:7,11:12,12:10,13:10,14:10,15:14,16:20,17:28,18:32}
TASK_TARGET = {
    "assessment_selection":47,
    "device_selection":9,
    "fact_recall":6,
    "finding_interpretation":79,
    "functional_goal_decision":20,
    "intervention_selection":46,
    "prognosis_prediction":16,
    "safety_priority":34,
}
LEVEL_TARGET = {1:6,2:80,3:116,4:55}
NODE_SLOT_TARGET = {"singleton_second":179,"multi_reinforcement":57,"new_node":21}
STRONG_TARGET = 224
SAFETY_AUGMENT_TARGET = 79
CATEGORY_NAMES = {1:"解剖学",2:"生理学",3:"心理学",4:"人間発達学",5:"教育学",6:"医学概論",7:"病理学",8:"内科学",9:"神経医学",10:"精神医学",11:"小児学",12:"臨床心理学",13:"基礎運動学",14:"臨床運動学",15:"動作分析学",16:"運動器",17:"理学療法評価各論",18:"理学療法治療各論"}


def read(name: str):
    return json.loads((BANK / name).read_text(encoding="utf-8-sig"))


def qnum(qid: str) -> int:
    return int(str(qid).removeprefix("Q"))


def build_report() -> dict:
    manifest = read("bank_manifest.json")
    if manifest["question_count"] != CURRENT_END or manifest["last_question_number"] != CURRENT_END:
        raise ValueError(f"unexpected live bank: {manifest}")

    questions = {row["id"]: row for row in read("questions.json")}
    tags = {row["id"]: row for row in read("question_tags.json")}
    nodes = {row["knowledge_node_id"]: row for row in read("knowledge_nodes.json")}
    added_qids = [f"Q{n}" for n in range(BASE_END + 1, CURRENT_END + 1)]
    if any(qid not in questions or qid not in tags for qid in added_qids):
        raise ValueError("Q1738-Q1761 missing from formal stores")
    added = [tags[qid] for qid in added_qids]
    if any(row.get("source") != "original" for row in added):
        raise ValueError("Q1738-Q1761 must all be original")

    category_used = Counter(int(questions[row["id"]]["category_small"]) for row in added)
    task_used = Counter(str(row["task"]) for row in added)
    level_used = Counter(int(row["level"]) for row in added)
    safety_used = Counter(str(row["safety"]) for row in added)
    slot_used = Counter()
    strong_used = 0
    weak = []

    for row in added:
        qid = row["id"]
        node_id = row["knowledge_node_id"]
        node = nodes[node_id]
        prior = [x for x in node.get("question_ids", []) if qnum(x) <= BASE_END]
        if len(prior) == 0:
            slot_used["new_node"] += 1
        elif len(prior) == 1:
            slot_used["singleton_second"] += 1
        else:
            slot_used["multi_reinforcement"] += 1
        demand = (row.get("task"), row.get("primary_ability"))
        if any(p in tags and (tags[p].get("task"), tags[p].get("primary_ability")) != demand for p in prior):
            strong_used += 1
        else:
            weak.append({"qid":qid,"node":node_id,"prior":prior,"demand":demand})

    category_remaining = {k:CATEGORY_TARGET[k]-category_used.get(k,0) for k in CATEGORY_TARGET}
    task_remaining = {k:TASK_TARGET[k]-task_used.get(k,0) for k in TASK_TARGET}
    level_remaining = {k:LEVEL_TARGET[k]-level_used.get(k,0) for k in LEVEL_TARGET}
    slot_remaining = {k:NODE_SLOT_TARGET[k]-slot_used.get(k,0) for k in NODE_SLOT_TARGET}
    safety_aug_used = safety_used.get("moderate",0) + safety_used.get("critical",0)

    for label, values in (("category",category_remaining),("task",task_remaining),("level",level_remaining),("slot",slot_remaining)):
        if any(v < 0 for v in values.values()):
            raise ValueError(f"{label} target overspent: {values}")

    original_remaining = sum(category_remaining.values())
    if original_remaining != 233:
        raise ValueError(f"expected 233 original remaining, got {original_remaining}")
    if sum(task_remaining.values()) != 233 or sum(level_remaining.values()) != 233 or sum(slot_remaining.values()) != 233:
        raise ValueError("remaining allocation dimensions do not sum to 233")
    total_remaining = FINAL_TARGET - CURRENT_END
    past_exam_remaining = total_remaining - original_remaining
    if past_exam_remaining != 6:
        raise ValueError(f"expected 6 past_exam remaining, got {past_exam_remaining}")

    return {
        "baseline_audit_end":BASE_END,
        "current_formal_end":CURRENT_END,
        "current_formal_count":CURRENT_END,
        "formal_original_added_since_audit":len(added_qids),
        "original_remaining":original_remaining,
        "past_exam_remaining":past_exam_remaining,
        "total_remaining":total_remaining,
        "used":{
            "category":dict(sorted(category_used.items())),
            "task":dict(sorted(task_used.items())),
            "level":dict(sorted(level_used.items())),
            "safety":dict(sorted(safety_used.items())),
            "node_slot":dict(sorted(slot_used.items())),
            "strong_formations":strong_used,
            "weak_or_unproven_formations":weak,
            "safety_augment":safety_aug_used,
        },
        "remaining_original_plan":{
            "category":category_remaining,
            "task":task_remaining,
            "level":level_remaining,
            "node_slot":slot_remaining,
            "strong_formations":STRONG_TARGET-strong_used,
            "safety_augment":SAFETY_AUGMENT_TARGET-safety_aug_used,
        },
        "production_lots":[48,48,48,48,41],
    }


def write_outputs(report: dict) -> None:
    (ROOT / "reports" / "question_bank_2000_remaining_allocation_v01.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    used = report["used"]
    rem = report["remaining_original_plan"]
    lines = [
        "# Question Bank 2000 — Remaining allocation v01","",
        f"Current formal bank: Q1-Q{CURRENT_END} / {CURRENT_END} questions.",
        f"Remaining to 2000: {report['total_remaining']} = original {report['original_remaining']} + past_exam {report['past_exam_remaining']}.","",
        "## Remaining original allocation by category","",
        "| ID | Category | Target +257 | Used Q1738-Q1761 | Remaining |","|---:|---|---:|---:|---:|",
    ]
    for cid in range(1,19):
        lines.append(f"| {cid} | {CATEGORY_NAMES[cid]} | {CATEGORY_TARGET[cid]} | {used['category'].get(str(cid),used['category'].get(cid,0))} | {rem['category'][cid]} |")
    lines += ["","## Remaining by task","","| Task | Target | Used | Remaining |","|---|---:|---:|---:|"]
    for key,target in TASK_TARGET.items():
        lines.append(f"| {key} | {target} | {used['task'].get(key,0)} | {rem['task'][key]} |")
    lines += ["","## Remaining by level","","| Level | Target | Used | Remaining |","|---:|---:|---:|---:|"]
    for level,target in LEVEL_TARGET.items():
        lines.append(f"| {level} | {target} | {used['level'].get(str(level),used['level'].get(level,0))} | {rem['level'][level]} |")
    lines += [
        "","## Node / repair supply","",
        f"- singleton-second remaining: {rem['node_slot']['singleton_second']}",
        f"- multi reinforcement remaining: {rem['node_slot']['multi_reinforcement']}",
        f"- new Node remaining: {rem['node_slot']['new_node']}",
        f"- strong formations remaining: {rem['strong_formations']}",
        f"- Safety moderate/critical augmentation remaining: {rem['safety_augment']}","",
        "## Production lots","",
        "Calibration is complete. Remaining originals are grouped into production lots: 48 / 48 / 48 / 48 / 41, followed by a separate 6-question past-exam acceptance step.","",
        "Each lot is staging-first, then formal integration only after semantic/duplicate/Node/category validation and full CI.",
    ]
    if used["weak_or_unproven_formations"]:
        lines += ["","## Warning","",f"{len(used['weak_or_unproven_formations'])} calibration additions did not prove a strong pair under the metadata rule and require inspection."]
    else:
        lines += ["","All 24 calibration additions prove a different-demand strong pair against at least one pre-audit question in their Node."]
    (ROOT / "docs" / "question-bank-2000-remaining-allocation-v01.md").write_text("\n".join(lines)+"\n",encoding="utf-8")


if __name__ == "__main__":
    report = build_report()
    write_outputs(report)
    print(json.dumps(report,ensure_ascii=False,indent=2))
