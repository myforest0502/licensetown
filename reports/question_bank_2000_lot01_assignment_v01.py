"""Create a quota-exact *suggested* demand/level/Safety assignment for Lot01.

This is an authoring aid, not an editorial approval. Existing-Node assignments are
forbidden from reusing an already-present (task, primary_ability) demand. The
optimizer uses light label/category heuristics only; medical authoring may replace
an assignment while preserving all lot quotas and validator rules.
"""
from __future__ import annotations

import json
from collections import Counter
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROSTER = ROOT / "reports" / "question_bank_2000_lot01_targets_v01.json"
OUT = ROOT / "reports" / "question_bank_2000_lot01_assignment_v01.json"

TASK_PRIMARY = {
    "assessment_selection":"MEASURE",
    "device_selection":"PRESCRIBE",
    "fact_recall":"KNOW",
    "finding_interpretation":"INTERPRET",
    "functional_goal_decision":"DECIDE",
    "intervention_selection":"PRESCRIBE",
    "prognosis_prediction":"PREDICT",
    "safety_priority":"DECIDE",
}
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
LEVEL_QUOTA = {1:1,2:16,3:20,4:11}
SAFETY_AUGMENT = 12

EVAL_WORDS = ("評価","検査","尺度","スコア","測定","MMT","筋力","ROM","歩行","血圧","反射")
DEVICE_WORDS = ("装具","車椅子","義足","杖","歩行器","電気刺激","機器","足部","スプリント")
INTERVENTION_WORDS = ("治療","訓練","運動","介助","管理","予防","除圧","調整","指導","リハ")
PROGNOSIS_WORDS = ("予後","回復","骨癒合","再発","進行","重症度")
SAFETY_WORDS = ("過反射","骨折","脱臼","心停止","呼吸","低酸素","出血","感染","塞栓","転倒","危険","中止","緊急","けいれん","てんかん","脊髄損傷")
FINDING_WORDS = ("所見","特徴","症状","徴候","障害","病変","麻痺","眼振","感覚","疼痛","筋萎縮")
GOAL_WORDS = ("ADL","生活","復帰","目標","活動","参加")


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def score_task(label: str, category: int, task: str, is_new: bool) -> int:
    text = str(label or "")
    score = 0
    if task == "finding_interpretation":
        score += 5 + 2 * sum(word in text for word in FINDING_WORDS)
        if category == 9:
            score += 2
    elif task == "assessment_selection":
        score += 3 + 3 * sum(word in text for word in EVAL_WORDS)
        if category == 17:
            score += 5
    elif task == "intervention_selection":
        score += 3 + 3 * sum(word in text for word in INTERVENTION_WORDS)
        if category == 18:
            score += 5
    elif task == "device_selection":
        score += 4 * sum(word in text for word in DEVICE_WORDS)
        if category in {16,18}:
            score += 2
    elif task == "safety_priority":
        score += 5 * sum(word in text for word in SAFETY_WORDS)
        if category in {9,16,18}:
            score += 1
    elif task == "prognosis_prediction":
        score += 4 * sum(word in text for word in PROGNOSIS_WORDS)
        if category in {9,16}:
            score += 1
    elif task == "functional_goal_decision":
        score += 3 * sum(word in text for word in GOAL_WORDS)
        if category in {17,18}:
            score += 2
    elif task == "fact_recall":
        score += 1
        if is_new:
            score += 1
    return score


def allowed_tasks(row: dict) -> list[str]:
    existing = {(str(x["task"]), str(x["primary_ability"])) for x in row.get("existing_demands", [])}
    return [task for task, ability in TASK_PRIMARY.items() if (task, ability) not in existing]


def main() -> int:
    roster = read(ROSTER)
    rows = []
    for target in roster["existing_node_targets"]:
        rows.append({
            "draft_id": target["lot_target_id"],
            "slot_type": target["slot_type"],
            "category_small": int(target["category_small"]),
            "label": target["label"],
            "target_node_id": target["canonical_node_id"],
            "reference_question_ids": target["question_ids"],
            "existing_demands": target.get("existing_demands", []),
            "is_new": False,
        })
    for reservation in roster["new_node_reservations"]:
        category = int(reservation["category_small"])
        rows.append({
            "draft_id": f"L01-C{category}-N01",
            "slot_type": "new_node",
            "category_small": category,
            "label": f"new Node concept in category {category}",
            "target_node_id": None,
            "reference_question_ids": [],
            "existing_demands": [],
            "is_new": True,
        })
    if len(rows) != 48:
        raise ValueError(f"expected 48 rows, got {len(rows)}")

    # Hardest rows first: fewer legal tasks, then existing targets before new slots.
    order = sorted(range(len(rows)), key=lambda i: (len(allowed_tasks(rows[i])), rows[i]["is_new"], rows[i]["draft_id"]))
    tasks = list(TASK_QUOTA)
    initial = tuple(TASK_QUOTA[t] for t in tasks)

    @lru_cache(maxsize=None)
    def solve(pos: int, remaining: tuple[int, ...]):
        if pos == len(order):
            return (0, ()) if not any(remaining) else None
        idx = order[pos]
        row = rows[idx]
        options = []
        legal = set(allowed_tasks(row))
        for ti, task in enumerate(tasks):
            if remaining[ti] <= 0 or task not in legal:
                continue
            new_remaining = list(remaining)
            new_remaining[ti] -= 1
            tail = solve(pos + 1, tuple(new_remaining))
            if tail is None:
                continue
            local = score_task(row["label"], row["category_small"], task, row["is_new"])
            options.append((local + tail[0], (task,) + tail[1]))
        return max(options, default=None, key=lambda x:x[0])

    solution = solve(0, initial)
    if solution is None:
        raise ValueError("no quota-exact task assignment exists under distinct-demand constraints")
    assignment_by_idx = {}
    for idx, task in zip(order, solution[1]):
        assignment_by_idx[idx] = task

    # Fact recall gets the only Level1 slot. Safety/prognosis are preferentially high-level;
    # remaining levels are assigned deterministically while respecting exact totals.
    level_remaining = Counter(LEVEL_QUOTA)
    task_priority_level = {
        "fact_recall":[1,2,3,4],
        "safety_priority":[4,3,2,1],
        "prognosis_prediction":[4,3,2,1],
        "functional_goal_decision":[3,4,2,1],
        "finding_interpretation":[3,2,4,1],
        "intervention_selection":[3,2,4,1],
        "assessment_selection":[2,3,4,1],
        "device_selection":[2,3,4,1],
    }
    for idx in sorted(range(len(rows)), key=lambda i:(assignment_by_idx[i] != "fact_recall", assignment_by_idx[i] != "safety_priority", rows[i]["draft_id"])):
        task = assignment_by_idx[idx]
        for level in task_priority_level[task]:
            if level_remaining[level] > 0:
                rows[idx]["suggested_level"] = level
                level_remaining[level] -= 1
                break
    if any(level_remaining.values()):
        raise ValueError(f"level assignment incomplete: {level_remaining}")

    # Safety: all six safety_priority drafts plus six highest-risk labels among the rest.
    safety_task_indices = [i for i in range(len(rows)) if assignment_by_idx[i] == "safety_priority"]
    risk_candidates = []
    for i,row in enumerate(rows):
        if i in safety_task_indices:
            continue
        risk = sum(word in str(row["label"]) for word in SAFETY_WORDS)
        risk_candidates.append((risk, row["category_small"] in {9,16,18}, -i, i))
    extra_safety = {item[-1] for item in sorted(risk_candidates, reverse=True)[:SAFETY_AUGMENT-len(safety_task_indices)]}

    output_rows = []
    for i,row in enumerate(rows):
        task = assignment_by_idx[i]
        safety = "critical" if task == "safety_priority" else ("moderate" if i in extra_safety else "none")
        output_rows.append({
            **row,
            "suggested_task": task,
            "suggested_primary_ability": TASK_PRIMARY[task],
            "suggested_level": row["suggested_level"],
            "suggested_safety": safety,
            "assignment_status": "authoring_suggestion_only",
            "author_may_replace": True,
        })

    task_counts = Counter(r["suggested_task"] for r in output_rows)
    level_counts = Counter(r["suggested_level"] for r in output_rows)
    safety_count = sum(r["suggested_safety"] in {"moderate","critical"} for r in output_rows)
    strong_structural = sum(
        (r["suggested_task"], r["suggested_primary_ability"]) not in {(x["task"],x["primary_ability"]) for x in r["existing_demands"]}
        for r in output_rows if not r["is_new"]
    )
    if task_counts != Counter(TASK_QUOTA) or level_counts != Counter(LEVEL_QUOTA):
        raise ValueError(f"quota mismatch tasks={task_counts} levels={level_counts}")
    if safety_count != SAFETY_AUGMENT:
        raise ValueError(f"Safety assignment mismatch: {safety_count}")
    if strong_structural != 44:
        raise ValueError(f"all 44 existing targets should have a structurally distinct demand, got {strong_structural}")

    payload = {
        "lot":1,
        "status":"authoring_suggestions_only",
        "formal_baseline":"Q1-Q1761",
        "optimizer_score":solution[0],
        "task_counts":dict(task_counts),
        "level_counts":dict(level_counts),
        "safety_moderate_or_critical":safety_count,
        "structurally_distinct_existing_assignments":strong_structural,
        "assignments":output_rows,
        "warning":"These are quota-exact structural suggestions, not medical/editorial approval. Authoring may change them if all final quotas and validator gates remain satisfied.",
    }
    OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:payload[k] for k in ("optimizer_score","task_counts","level_counts","safety_moderate_or_critical","structurally_distinct_existing_assignments")},ensure_ascii=False,indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
