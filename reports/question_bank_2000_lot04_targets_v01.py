"""Select deterministic existing-Node targets for Question Bank 2000 production Lot04.

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
FORMAL_BASELINE_END = 1905
RECENT_EXCLUDE_AFTER = 1857
EXCLUDE_NODE = "KN0779"

CATEGORY_SLOT = {
    1: {"singleton": 2, "multi": 1, "new": 1},
    2: {"singleton": 3, "multi": 1, "new": 1},
    3: {"singleton": 1, "multi": 1, "new": 0},
    4: {"singleton": 1, "multi": 1, "new": 0},
    5: {"singleton": 1, "multi": 1, "new": 0},
    6: {"singleton": 2, "multi": 1, "new": 0},
    7: {"singleton": 2, "multi": 1, "new": 0},
    8: {"singleton": 3, "multi": 2, "new": 1},
    9: {"singleton": 1, "multi": 1, "new": 0},
    10: {"singleton": 1, "multi": 1, "new": 0},
    11: {"singleton": 2, "multi": 1, "new": 0},
    12: {"singleton": 1, "multi": 1, "new": 0},
    13: {"singleton": 2, "multi": 1, "new": 0},
    14: {"singleton": 1, "multi": 1, "new": 0},
    15: {"singleton": 2, "multi": 1, "new": 1},
    17: {"singleton": 1, "multi": 0, "new": 0},
    18: {"singleton": 1, "multi": 1, "new": 0},
}
TARGET_MULTI_TOTAL = 17
TARGET_SINGLETON_TOTAL = 27
TARGET_NEW_TOTAL = 4


def read(name: str):
    return json.loads((BANK / name).read_text(encoding="utf-8-sig"))


def qnum(qid: str) -> int:
    return int(str(qid).removeprefix("Q"))


def _solve_slot_split(inventory: dict) -> dict[int, dict[str, int]]:
    categories = tuple(CATEGORY_SLOT)
    bounds = {}
    for category in categories:
        planned = CATEGORY_SLOT[category]
        existing_total = planned["singleton"] + planned["multi"]
        singleton_available = len(inventory[category]["singleton"])
        multi_available = len(inventory[category]["multi"])
        min_multi = max(0, existing_total - singleton_available)
        max_multi = min(existing_total, multi_available)
        if min_multi > max_multi:
            raise ValueError(
                f"category {category} lacks total existing-Node inventory: "
                f"need {existing_total}, singleton={singleton_available}, multi={multi_available}"
            )
        bounds[category] = (min_multi, max_multi)

    @lru_cache(maxsize=None)
    def solve(pos: int, remaining_multi: int):
        if pos == len(categories):
            return (0, ()) if remaining_multi == 0 else None
        category = categories[pos]
        preferred = CATEGORY_SLOT[category]["multi"]
        lo, hi = bounds[category]
        best = None
        for multi in range(lo, hi + 1):
            if multi > remaining_multi:
                break
            tail = solve(pos + 1, remaining_multi - multi)
            if tail is None:
                continue
            score = -abs(multi - preferred) + tail[0]
            candidate = (score, (multi,) + tail[1])
            if best is None or candidate[0] > best[0] or (
                candidate[0] == best[0] and candidate[1] < best[1]
            ):
                best = candidate
        return best

    solution = solve(0, TARGET_MULTI_TOTAL)
    if solution is None:
        detail = {
            c: {
                "existing_required": CATEGORY_SLOT[c]["singleton"] + CATEGORY_SLOT[c]["multi"],
                "singleton_available": len(inventory[c]["singleton"]),
                "multi_available": len(inventory[c]["multi"]),
                "multi_bounds": bounds[c],
            }
            for c in categories
        }
        raise ValueError(f"no feasible Lot04 27/17 Node-slot allocation: {detail}")

    actual = {}
    for category, multi in zip(categories, solution[1]):
        existing_total = CATEGORY_SLOT[category]["singleton"] + CATEGORY_SLOT[category]["multi"]
        actual[category] = {
            "singleton": existing_total - multi,
            "multi": multi,
            "new": CATEGORY_SLOT[category]["new"],
        }
    if sum(v["singleton"] for v in actual.values()) != TARGET_SINGLETON_TOTAL:
        raise ValueError(f"inventory-aware singleton total is not {TARGET_SINGLETON_TOTAL}: {actual}")
    if sum(v["multi"] for v in actual.values()) != TARGET_MULTI_TOTAL:
        raise ValueError(f"inventory-aware multi total is not {TARGET_MULTI_TOTAL}: {actual}")
    if sum(v["new"] for v in actual.values()) != TARGET_NEW_TOTAL:
        raise ValueError(f"new Node total is not {TARGET_NEW_TOTAL}: {actual}")
    return actual


def main() -> int:
    questions = {row["id"]: row for row in read("questions.json")}
    tags = {row["id"]: row for row in read("question_tags.json")}
    nodes = {row["knowledge_node_id"]: row for row in read("knowledge_nodes.json")}
    cmap = read("knowledge_node_canonical_map.json")

    if max(map(qnum, questions)) != FORMAL_BASELINE_END:
        raise ValueError(
            f"Lot04 selector requires formal Q1-Q{FORMAL_BASELINE_END}; "
            f"found max Q{max(map(qnum, questions))}"
        )
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

    inventory = {cid: {"singleton": [], "multi": []} for cid in CATEGORY_SLOT}
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
        if category not in CATEGORY_SLOT:
            continue

        demands = sorted({(str(tags[qid]["task"]), str(tags[qid]["primary_ability"])) for qid in qids})
        sources = Counter(str(tags[qid]["source"]) for qid in qids)
        levels = sorted({int(tags[qid]["level"]) for qid in qids})
        safeties = sorted({str(tags[qid]["safety"]) for qid in qids})
        registry = nodes.get(node_id, {})
        record = {
            "canonical_node_id": node_id,
            "label": registry.get("label") or tags[qids[0]].get("knowledge_node"),
            "category_small": category,
            "question_ids": qids,
            "existing_demands": [{"task": task, "primary_ability": ability} for task, ability in demands],
            "sources": dict(sources),
            "levels": levels,
            "safety": safeties,
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
            record["selection_intent"] = "add a clinically distinct second demand; candidate must not repeat the reference task/ability"
            inventory[category]["singleton"].append((score, record))
        else:
            weak_multi = len(demands) == 1
            past_exam_count = sources.get("past_exam", 0)
            score = (1 if weak_multi else 0, -len(qids), past_exam_count, -qnum(qids[0]))
            record["rank_score"] = list(score)
            record["selection_intent"] = "add a demand outside the existing demand set; weak multi Nodes are preferred"
            record["currently_weak_by_metadata"] = weak_multi
            inventory[category]["multi"].append((score, record))

    actual_slot = _solve_slot_split(inventory)
    selected = []
    summary = {}
    for category, quota in actual_slot.items():
        summary[category] = {}
        for kind in ("singleton", "multi"):
            ranked = sorted(inventory[category][kind], key=lambda item: item[0], reverse=True)
            need = quota[kind]
            picks = [record for _, record in ranked[:need]]
            for index, record in enumerate(picks, start=1):
                row = dict(record)
                row["slot_type"] = "singleton_second" if kind == "singleton" else "multi_reinforcement"
                row["lot_target_id"] = f"L04-C{category}-{kind[:1].upper()}{index:02d}"
                selected.append(row)
            summary[category][kind] = {"available": len(ranked), "selected": need}
        summary[category]["new_node_reserved"] = quota["new"]
        summary[category]["preferred_split"] = CATEGORY_SLOT[category]

    if len(selected) != 44 or len({row["canonical_node_id"] for row in selected}) != 44:
        raise ValueError("Lot04 existing-Node selection must be 44 unique canonical Nodes")
    slot_counts = Counter(row["slot_type"] for row in selected)
    if slot_counts != Counter({"singleton_second": 27, "multi_reinforcement": 17}):
        raise ValueError(f"unexpected slot counts: {slot_counts}")

    category_question_totals = {
        category: quota["singleton"] + quota["multi"] + quota["new"]
        for category, quota in actual_slot.items()
    }
    expected_category_totals = {1: 4, 2: 5, 3: 2, 4: 2, 5: 2, 6: 3, 7: 3, 8: 6, 9: 2, 10: 2, 11: 3, 12: 2, 13: 3, 14: 2, 15: 4, 17: 1, 18: 2}
    if category_question_totals != expected_category_totals:
        raise ValueError(f"Lot04 category totals mismatch: {category_question_totals}")

    output = {
        "lot": 4,
        "formal_baseline": "Q1-Q1905",
        "scope": "structural_target_selection_only",
        "recent_node_exclusion_after_q": RECENT_EXCLUDE_AFTER,
        "preferred_category_slot": CATEGORY_SLOT,
        "actual_category_slot": actual_slot,
        "existing_node_targets": selected,
        "new_node_reservations": [
            {"category_small": category, "count": quota["new"], "node_id_allocated": False}
            for category, quota in actual_slot.items() if quota["new"]
        ],
        "inventory_summary": summary,
        "excluded_recent_node_count": len(excluded_recent_nodes),
        "required_existing_targets": 44,
        "required_new_nodes": 4,
        "required_total_questions": 48,
        "required_strong_formations": 37,
        "required_safety_augment": 12,
        "guardrails": [
            "No Q IDs are allocated by this target roster.",
            "No Knowledge Node registry write is performed.",
            "Nodes receiving Lot03 supply after Q1857 are not immediately retargeted.",
            "Per-category singleton/multi split may rebalance only when formal inventory requires it; global 27/17 and category totals remain exact.",
            "Every singleton draft must differ from the reference in task or primary ability and semantic demand.",
            "Every multi-reinforcement draft intended as strong must add a demand not already present in that Node.",
            "A target may be replaced from the same category/slot inventory during medical/semantic review."
        ]
    }
    out = ROOT / "reports" / "question_bank_2000_lot04_targets_v01.json"
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "selected": len(selected),
        "slot_counts": dict(slot_counts),
        "actual_category_slot": actual_slot,
        "category_question_totals": category_question_totals,
        "excluded_recent_node_count": len(excluded_recent_nodes),
        "inventory_summary": summary
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
