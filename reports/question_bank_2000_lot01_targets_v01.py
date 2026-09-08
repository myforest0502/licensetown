"""Select deterministic existing-Node targets for Question Bank 2000 production Lot 01.

This is structural target selection only. It does not draft questions, create new Nodes,
allocate Q IDs, or modify formal data.
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BANK = ROOT / "data" / "question_bank"
BASE_AUDIT_END = 1737
EXCLUDE_NODE = "KN0779"
CATEGORY_SLOT = {
    9: {"singleton": 8, "multi": 3, "new": 1},
    16: {"singleton": 7, "multi": 2, "new": 1},
    17: {"singleton": 8, "multi": 3, "new": 1},
    18: {"singleton": 9, "multi": 4, "new": 1},
}


def read(name: str):
    return json.loads((BANK / name).read_text(encoding="utf-8-sig"))


def qnum(qid: str) -> int:
    return int(str(qid).removeprefix("Q"))


def main() -> int:
    questions = {row["id"]: row for row in read("questions.json")}
    tags = {row["id"]: row for row in read("question_tags.json")}
    nodes = {row["knowledge_node_id"]: row for row in read("knowledge_nodes.json")}
    cmap = read("knowledge_node_canonical_map.json")
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
    for node_id, qids in groups.items():
        if node_id == canonical(EXCLUDE_NODE):
            continue
        # Calibration Nodes already touched after the Q1737 audit are not targeted again in Lot 01.
        if any(qnum(qid) > BASE_AUDIT_END for qid in qids):
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
            # Prefer singleton Nodes whose only supply is recall/past-exam/basic, because an
            # applied second question can add the largest repair value. Tie-break deterministically.
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
            # Prefer weak/same-demand multi Nodes first, then smallest groups. A new demand
            # can convert under-supplied multi Nodes into strong repair supply.
            weak_multi = len(demands) == 1
            past_exam_count = sources.get("past_exam", 0)
            score = (1 if weak_multi else 0, -len(qids), past_exam_count, -qnum(qids[0]))
            record["rank_score"] = list(score)
            record["selection_intent"] = "add a demand outside the existing demand set; weak multi Nodes are preferred"
            record["currently_weak_by_metadata"] = weak_multi
            inventory[category]["multi"].append((score, record))

    selected = []
    summary = {}
    for category, quota in CATEGORY_SLOT.items():
        summary[category] = {}
        for kind in ("singleton", "multi"):
            ranked = sorted(inventory[category][kind], key=lambda item: item[0], reverse=True)
            need = quota[kind]
            if len(ranked) < need:
                raise ValueError(f"category {category} lacks {kind} inventory: need {need}, have {len(ranked)}")
            picks = [record for _, record in ranked[:need]]
            for index, record in enumerate(picks, start=1):
                record = dict(record)
                record["slot_type"] = "singleton_second" if kind == "singleton" else "multi_reinforcement"
                record["lot_target_id"] = f"L01-C{category}-{kind[:1].upper()}{index:02d}"
                selected.append(record)
            summary[category][kind] = {
                "available": len(ranked),
                "selected": need,
            }
        summary[category]["new_node_reserved"] = quota["new"]

    if len(selected) != 44 or len({row["canonical_node_id"] for row in selected}) != 44:
        raise ValueError("Lot01 existing-Node selection must be 44 unique canonical Nodes")
    slot_counts = Counter(row["slot_type"] for row in selected)
    if slot_counts != Counter({"singleton_second": 32, "multi_reinforcement": 12}):
        raise ValueError(f"unexpected slot counts: {slot_counts}")

    output = {
        "lot": 1,
        "formal_baseline": "Q1-Q1761",
        "scope": "structural_target_selection_only",
        "existing_node_targets": selected,
        "new_node_reservations": [
            {"category_small": category, "count": quota["new"], "node_id_allocated": False}
            for category, quota in CATEGORY_SLOT.items()
        ],
        "inventory_summary": summary,
        "required_existing_targets": 44,
        "required_new_nodes": 4,
        "required_total_questions": 48,
        "required_strong_formations": 41,
        "required_safety_augment": 12,
        "guardrails": [
            "No Q IDs are allocated by this target roster.",
            "No Knowledge Node registry write is performed.",
            "Every singleton draft must differ from the reference in task or primary ability and in semantic demand.",
            "Every multi-reinforcement draft intended as strong must add a demand not already present in that Node.",
            "A selected target may still be rejected during medical/semantic drafting review and replaced from the same category/slot inventory.",
        ],
    }
    out = ROOT / "reports" / "question_bank_2000_lot01_targets_v01.json"
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "selected": len(selected),
        "slot_counts": dict(slot_counts),
        "categories": {str(c): {"singleton": q["singleton"], "multi": q["multi"], "new": q["new"]} for c, q in CATEGORY_SLOT.items()},
        "inventory_summary": summary,
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
