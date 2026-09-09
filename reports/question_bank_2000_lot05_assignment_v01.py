"""Assign exact task/level quotas to the deterministic Lot05 target roster.

This is an authoring plan only. It does not write formal Question Bank data.
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGETS = ROOT / "reports" / "question_bank_2000_lot05_targets_v01.json"
OUT = ROOT / "reports" / "question_bank_2000_lot05_assignment_v01.json"

TASK_TO_ABILITY = {
    "assessment_selection": "MEASURE",
    "device_selection": "PRESCRIBE",
    "fact_recall": "KNOW",
    "finding_interpretation": "INTERPRET",
    "functional_goal_decision": "DECIDE",
    "intervention_selection": "PRESCRIBE",
    "prognosis_prediction": "PREDICT",
    "safety_priority": "DECIDE",
}

TASK_KEYWORDS = {
    "assessment_selection": ("評価", "検査", "測定", "尺度", "スコア", "診断", "感度", "ICF"),
    "device_selection": ("装具", "車椅子", "杖", "義足", "福祉用具"),
    "fact_recall": ("神経支配", "付着", "酵素", "解剖", "生理", "定義"),
    "finding_interpretation": ("所見", "症候", "特徴", "病態", "伝導路", "脳血管", "認知", "発達"),
    "functional_goal_decision": ("活動", "参加", "教育", "生活", "発達", "ICF"),
    "intervention_selection": ("治療", "運動", "訓練", "介入", "対応", "支援"),
    "prognosis_prediction": ("予後", "進行", "回復", "成人期", "老年期", "発達"),
    "safety_priority": ("危険", "禁忌", "急性", "重症", "循環", "呼吸", "感染", "転倒"),
}

PREFERRED_LEVEL = {
    "fact_recall": 1,
    "assessment_selection": 2,
    "device_selection": 2,
    "finding_interpretation": 3,
    "functional_goal_decision": 3,
    "intervention_selection": 3,
    "prognosis_prediction": 4,
    "safety_priority": 4,
}


def load():
    return json.loads(TARGETS.read_text(encoding="utf-8"))


def score_task(row: dict, task: str) -> tuple:
    label = str(row.get("label") or row.get("target_node_label") or "")
    hits = sum(word in label for word in TASK_KEYWORDS[task])
    slot = row.get("slot_type")
    # Favor clinically useful higher-order demands for existing Nodes and reserve
    # direct recall for the single required slot.
    higher = 1 if task not in {"fact_recall"} else 0
    safety_hint = 1 if task == "safety_priority" and any(x in label for x in TASK_KEYWORDS["safety_priority"]) else 0
    singleton_bonus = 1 if slot == "singleton_second" and task in {"finding_interpretation", "assessment_selection", "intervention_selection"} else 0
    return (hits, safety_hint, singleton_bonus, higher)


def compatible(row: dict, task: str) -> bool:
    demand = (task, TASK_TO_ABILITY[task])
    existing = {(x["task"], x["primary_ability"]) for x in row.get("existing_demands", [])}
    return demand not in existing


def assign_tasks(rows: list[dict], quota: dict[str, int]) -> list[dict]:
    remaining = dict(quota)
    result = []
    # Constrained rows first; ties favor rows with strongest keyword signal.
    ordered = sorted(
        rows,
        key=lambda r: (
            sum(compatible(r, t) for t in quota),
            -max(score_task(r, t) for t in quota if compatible(r, t))[0],
            str(r["draft_id"]),
        ),
    )
    for index, row in enumerate(ordered):
        candidates = [t for t, n in remaining.items() if n > 0 and compatible(row, t)]
        if not candidates:
            raise ValueError(f"no compatible task remains for {row['draft_id']}: {remaining}")
        # Keep rare quotas available by preferring a strong semantic score, then the
        # task with the largest remaining demand.
        task = max(candidates, key=lambda t: (score_task(row, t), remaining[t], t))
        remaining[task] -= 1
        out = dict(row)
        out["proposed_task"] = task
        out["primary_ability"] = TASK_TO_ABILITY[task]
        result.append(out)
    if any(remaining.values()):
        raise ValueError(f"task quotas not exhausted: {remaining}")
    return sorted(result, key=lambda r: r["draft_order"])


def assign_levels(rows: list[dict], quota: dict[str, int]) -> list[dict]:
    slots = []
    for level, count in sorted((int(k), int(v)) for k, v in quota.items()):
        slots.extend([level] * count)
    # Match each row greedily to the closest available level to its task preference.
    available = Counter(slots)
    out = []
    order = sorted(rows, key=lambda r: (PREFERRED_LEVEL[r["proposed_task"]], r["draft_order"]))
    for row in order:
        pref = PREFERRED_LEVEL[row["proposed_task"]]
        choices = [level for level, count in available.items() if count > 0]
        level = min(choices, key=lambda x: (abs(x - pref), x))
        available[level] -= 1
        copy = dict(row)
        copy["level"] = level
        out.append(copy)
    if any(available.values()):
        raise ValueError(f"level quotas not exhausted: {available}")
    return sorted(out, key=lambda r: r["draft_order"])


def main() -> int:
    targets = load()
    rows = []
    order = 1
    for row in targets["existing_node_targets"]:
        item = dict(row)
        item["draft_id"] = row["lot_target_id"]
        item["draft_order"] = order
        rows.append(item)
        order += 1
    for reservation in targets["new_node_reservations"]:
        for idx in range(int(reservation["count"])):
            category = int(reservation["category_small"])
            rows.append({
                "draft_id": f"L05-C{category}-N{idx+1:02d}",
                "draft_order": order,
                "slot_type": "new_node",
                "category_small": category,
                "canonical_node_id": None,
                "label": f"NEW_NODE_C{category}_PENDING_COLLISION_REVIEW",
                "question_ids": [],
                "existing_demands": [],
            })
            order += 1
    if len(rows) != 41:
        raise ValueError(f"expected 41 Lot05 rows, got {len(rows)}")

    assigned = assign_tasks(rows, targets["task_quota"])
    assigned = assign_levels(assigned, targets["level_quota"])
    task_counts = Counter(row["proposed_task"] for row in assigned)
    level_counts = Counter(str(row["level"]) for row in assigned)
    expected_task = Counter({k: int(v) for k, v in targets["task_quota"].items()})
    expected_level = Counter({str(k): int(v) for k, v in targets["level_quota"].items()})
    if task_counts != expected_task:
        raise ValueError(f"task count mismatch: {task_counts} != {expected_task}")
    if level_counts != expected_level:
        raise ValueError(f"level count mismatch: {level_counts} != {expected_level}")
    for row in assigned:
        if row["slot_type"] != "new_node" and not compatible(row, row["proposed_task"]):
            raise ValueError(f"duplicate demand assignment: {row['draft_id']}")

    payload = {
        "lot": 5,
        "formal_baseline": targets["formal_baseline"],
        "status": "authoring_assignment",
        "production_write": False,
        "db_write": False,
        "task_quota": targets["task_quota"],
        "level_quota": targets["level_quota"],
        "required_safety_augment": targets["required_safety_augment"],
        "required_strong_formations": targets["required_strong_formations"],
        "assignments": assigned,
        "guardrails": [
            "Assignment is a starting plan; medical/semantic review may swap tasks while exact final quotas remain fixed.",
            "Existing-Node rows must add a genuinely different semantic demand, not just different metadata.",
            "New Nodes remain unallocated until collision review is complete.",
        ],
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"task": dict(task_counts), "level": dict(level_counts)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
