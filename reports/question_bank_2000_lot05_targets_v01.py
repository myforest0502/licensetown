"""Select deterministic existing-Node targets for Question Bank 2000 production Lot05.

Structural target selection only. This script does not draft questions, create Nodes,
allocate formal Q IDs, or modify formal Question Bank data.
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BANK = ROOT / "data" / "question_bank"
FORMAL_BASELINE_END = 1953
RECENT_EXCLUDE_AFTER = 1737
EXCLUDE_NODE = "KN0779"

CATEGORY_TOTALS = {
    1: 4, 2: 5, 3: 1, 4: 2, 5: 1, 6: 2, 7: 3, 8: 5, 9: 1,
    10: 2, 11: 2, 12: 1, 13: 3, 14: 2, 15: 3, 16: 0, 17: 2, 18: 2,
}
# Three genuinely new concepts are reserved in foundational/pathology categories.
NEW_BY_CATEGORY = {1: 1, 2: 1, 7: 1}
TARGET_SINGLETON_TOTAL = 18
TARGET_MULTI_TOTAL = 20
TARGET_NEW_TOTAL = 3


def read(name: str):
    return json.loads((BANK / name).read_text(encoding="utf-8-sig"))


def qnum(qid: str) -> int:
    return int(str(qid).removeprefix("Q"))


def _preferred_multi(category: int, existing_total: int) -> int:
    # Final lot intentionally leans toward multi reinforcement while preserving
    # enough singleton-second supply to close the audited 18/20/3 slot plan.
    return min(existing_total, max(0, round(existing_total * TARGET_MULTI_TOTAL / (TARGET_MULTI_TOTAL + TARGET_SINGLETON_TOTAL))))


def _solve_slot_split(inventory: dict) -> dict[int, dict[str, int]]:
    categories = tuple(c for c, total in CATEGORY_TOTALS.items() if total)
    bounds = {}
    preferred = {}
    for category in categories:
        new_count = NEW_BY_CATEGORY.get(category, 0)
        existing_total = CATEGORY_TOTALS[category] - new_count
        singleton_available = len(inventory[category]["singleton"])
        multi_available = len(inventory[category]["multi"])
        min_multi = max(0, existing_total - singleton_available)
        max_multi = min(existing_total, multi_available)
        if min_multi > max_multi:
            raise ValueError(
                f"category {category} lacks existing-Node inventory: need {existing_total}, "
                f"singleton={singleton_available}, multi={multi_available}"
            )
        bounds[category] = (min_multi, max_multi)
        preferred[category] = _preferred_multi(category, existing_total)

    @lru_cache(maxsize=None)
    def solve(pos: int, remaining_multi: int):
        if pos == len(categories):
            return (0, ()) if remaining_multi == 0 else None
        category = categories[pos]
        lo, hi = bounds[category]
        best = None
        for multi in range(lo, hi + 1):
            if multi > remaining_multi:
                break
            tail = solve(pos + 1, remaining_multi - multi)
            if tail is None:
                continue
            score = -abs(multi - preferred[category]) + tail[0]
            candidate = (score, (multi,) + tail[1])
            if best is None or candidate[0] > best[0] or (candidate[0] == best[0] and candidate[1] < best[1]):
                best = candidate
        return best

    solution = solve(0, TARGET_MULTI_TOTAL)
    if solution is None:
        raise ValueError(f"no feasible Lot05 slot allocation: bounds={bounds}")

    actual = {}
    for category, multi in zip(categories, solution[1]):
        new_count = NEW_BY_CATEGORY.get(category, 0)
        existing_total = CATEGORY_TOTALS[category] - new_count
        actual[category] = {
            "singleton": existing_total - multi,
            "multi": multi,
            "new": new_count,
        }
    if sum(v["singleton"] for v in actual.values()) != TARGET_SINGLETON_TOTAL:
        raise ValueError(f"singleton total mismatch: {actual}")
    if sum(v["multi"] for v in actual.values()) != TARGET_MULTI_TOTAL:
        raise ValueError(f"multi total mismatch: {actual}")
    if sum(v["new"] for v in actual.values()) != TARGET_NEW_TOTAL:
        raise ValueError(f"new total mismatch: {actual}")
    return actual


def main() -> int:
    questions = {row["id"]: row for row in read("questions.json")}
    tags = {row["id"]: row for row in read("question_tags.json")}
    nodes = {row["knowledge_node_id"]: row for row in read("knowledge_nodes.json")}
    cmap = read("knowledge_node_canonical_map.json")

    if max(map(qnum, questions)) != FORMAL_BASELINE_END:
        raise ValueError(f"Lot05 selector requires Q1-Q{FORMAL_BASELINE_END}")
    if set(questions) != set(tags):
        raise ValueError("questions/question_tags ID sets differ")

    alias_to_canonical = {}
    for row in cmap:
        canonical = str(row["canonical_node_id"])
        alias_to_canonical[canonical] = canonical
        for alias in row.get("alias_node_ids", []):
            alias_to_canonical[str(alias)] = canonical

    def canonical(node_id: str) -> str:
        return alias_to_canonical.get(str(node_id), str(node_id))

    groups = defaultdict(list)
    for qid, tag in tags.items():
        groups[canonical(tag["knowledge_node_id"])].append(qid)
    for qids in groups.values():
        qids.sort(key=qnum)

    inventory = {cid: {"singleton": [], "multi": []} for cid in CATEGORY_TOTALS if CATEGORY_TOTALS[cid]}
    excluded_recent_nodes = set()
    for node_id, qids in groups.items():
        if node_id == canonical(EXCLUDE_NODE):
            continue
        if any(qnum(qid) > RECENT_EXCLUDE_AFTER for qid in qids):
            excluded_recent_nodes.add(node_id)
            continue
        categories = {int(questions[qid]["category_small"]) for qid in qids}
        if len(categories) != 1:
            continue
        category = next(iter(categories))
        if category not in inventory:
            continue
        demands = sorted({(str(tags[qid]["task"]), str(tags[qid]["primary_ability"])) for qid in qids})
        sources = Counter(str(tags[qid]["source"]) for qid in qids)
        registry = nodes.get(node_id, {})
        record = {
            "canonical_node_id": node_id,
            "label": registry.get("label") or tags[qids[0]].get("knowledge_node"),
            "category_small": category,
            "question_ids": qids,
            "existing_demands": [{"task": t, "primary_ability": a} for t, a in demands],
            "sources": dict(sources),
            "levels": sorted({int(tags[qid]["level"]) for qid in qids}),
            "safety": sorted({str(tags[qid]["safety"]) for qid in qids}),
        }
        if len(qids) == 1:
            tag = tags[qids[0]]
            score = (
                1 if tag.get("task") == "fact_recall" else 0,
                1 if tag.get("source") == "past_exam" else 0,
                1 if int(tag.get("level", 4)) <= 2 else 0,
                -qnum(qids[0]),
            )
            record["rank_score"] = list(score)
            inventory[category]["singleton"].append((score, record))
        else:
            weak_multi = len(demands) == 1
            score = (1 if weak_multi else 0, -len(qids), sources.get("past_exam", 0), -qnum(qids[0]))
            record["rank_score"] = list(score)
            record["currently_weak_by_metadata"] = weak_multi
            inventory[category]["multi"].append((score, record))

    actual = _solve_slot_split(inventory)
    selected = []
    summary = {}
    for category, quota in actual.items():
        summary[category] = {}
        for kind in ("singleton", "multi"):
            ranked = sorted(inventory[category][kind], key=lambda item: item[0], reverse=True)
            need = quota[kind]
            picks = [record for _, record in ranked[:need]]
            for index, record in enumerate(picks, start=1):
                row = dict(record)
                row["slot_type"] = "singleton_second" if kind == "singleton" else "multi_reinforcement"
                row["lot_target_id"] = f"L05-C{category}-{kind[:1].upper()}{index:02d}"
                selected.append(row)
            summary[category][kind] = {"available": len(ranked), "selected": need}
        summary[category]["new_node_reserved"] = quota["new"]

    if len(selected) != 38 or len({row["canonical_node_id"] for row in selected}) != 38:
        raise ValueError("Lot05 must select 38 unique existing canonical Nodes")
    slot_counts = Counter(row["slot_type"] for row in selected)
    expected_slots = Counter({"singleton_second": 18, "multi_reinforcement": 20})
    if slot_counts != expected_slots:
        raise ValueError(f"unexpected slot counts: {slot_counts}")

    output = {
        "lot": 5,
        "formal_baseline": "Q1-Q1953",
        "scope": "structural_target_selection_only",
        "recent_node_exclusion_after_q": RECENT_EXCLUDE_AFTER,
        "category_totals": CATEGORY_TOTALS,
        "new_node_by_category": NEW_BY_CATEGORY,
        "actual_category_slot": actual,
        "existing_node_targets": selected,
        "new_node_reservations": [
            {"category_small": c, "count": n, "node_id_allocated": False}
            for c, n in NEW_BY_CATEGORY.items()
        ],
        "inventory_summary": summary,
        "excluded_recent_node_count": len(excluded_recent_nodes),
        "required_existing_targets": 38,
        "required_new_nodes": 3,
        "required_total_questions": 41,
        "required_strong_formations": 26,
        "required_safety_augment": 11,
        "task_quota": {
            "assessment_selection": 7,
            "device_selection": 1,
            "fact_recall": 1,
            "finding_interpretation": 13,
            "functional_goal_decision": 4,
            "intervention_selection": 7,
            "prognosis_prediction": 3,
            "safety_priority": 5,
        },
        "level_quota": {"1": 1, "2": 13, "3": 18, "4": 9},
        "guardrails": [
            "No Q IDs are allocated by this target roster.",
            "No Knowledge Node registry write is performed.",
            "Nodes with questions added after Q1737 are excluded from immediate retargeting.",
            "Every existing-Node draft must add a distinct task/ability and semantic demand.",
            "New-node reservations require explicit collision review before Node ID allocation.",
        ],
    }
    out = ROOT / "reports" / "question_bank_2000_lot05_targets_v01.json"
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "selected": len(selected),
        "slot_counts": dict(slot_counts),
        "actual_category_slot": actual,
        "excluded_recent_node_count": len(excluded_recent_nodes),
        "inventory_summary": summary,
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
