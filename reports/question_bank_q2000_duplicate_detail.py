"""Detail exact normalized-stem duplicate groups in Q1-Q2000.

Read-only. This classifies same-stem groups by whether choices and accepted answers are also
identical so editorial repair can prioritize true duplicate records.
"""
from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BANK = ROOT / "data" / "question_bank"
OUT = ROOT / "reports" / "question_bank_q2000_duplicate_detail.json"


def load(name: str):
    return json.loads((BANK / name).read_text(encoding="utf-8-sig"))


def norm(value) -> str:
    text = str(value or "").lower()
    text = re.sub(r"\s+", "", text)
    return re.sub(r"[、。,.，．・:：;；!?！？()（）\[\]【】「」『』<>＜＞\-―ー]", "", text)


def choice_signature(q: dict):
    choices = q.get("choices") or q.get("options") or {}
    if isinstance(choices, dict):
        return tuple((str(k), norm(v)) for k, v in sorted(choices.items(), key=lambda kv: str(kv[0])))
    return tuple(norm(v) for v in choices) if isinstance(choices, list) else ()


def answer_signature(a: dict):
    sets = a.get("accepted_answer_sets") or []
    if sets:
        return tuple(sorted(tuple(sorted(str(x) for x in s)) for s in sets if isinstance(s, list)))
    return (str(a.get("display_answer") or a.get("answer") or ""),)


def main():
    qs = load("questions.json")
    ans = {x["id"]: x for x in load("answers.json")}
    tags = {x["id"]: x for x in load("question_tags.json")}
    groups = defaultdict(list)
    for q in qs:
        groups[norm(q.get("question_text"))].append(q)
    rows = []
    for _stem, items in groups.items():
        if len(items) < 2:
            continue
        item_rows = []
        for q in sorted(items, key=lambda x: int(x["id"][1:])):
            t = tags[q["id"]]
            item_rows.append({
                "id": q["id"],
                "question_text": q.get("question_text"),
                "choices": q.get("choices"),
                "accepted_answer_sets": ans[q["id"]].get("accepted_answer_sets"),
                "display_answer": ans[q["id"]].get("display_answer"),
                "answer_basis": ans[q["id"]].get("answer_basis"),
                "source": q.get("source"),
                "category_small": q.get("category_small"),
                "task": t.get("task"),
                "level": t.get("level"),
                "safety": t.get("safety"),
                "knowledge_node_id": t.get("knowledge_node_id"),
            })
        choice_sigs = {choice_signature(q) for q in items}
        answer_sigs = {answer_signature(ans[q["id"]]) for q in items}
        rows.append({
            "ids": [r["id"] for r in item_rows],
            "same_choices": len(choice_sigs) == 1,
            "same_answers": len(answer_sigs) == 1,
            "true_duplicate_signature": len(choice_sigs) == 1 and len(answer_sigs) == 1,
            "items": item_rows,
        })
    rows.sort(key=lambda x: (not x["true_duplicate_signature"], int(x["ids"][0][1:])))
    result = {
        "group_count": len(rows),
        "true_duplicate_signature_groups": sum(r["true_duplicate_signature"] for r in rows),
        "same_stem_but_different_signature_groups": sum(not r["true_duplicate_signature"] for r in rows),
        "groups": rows,
    }
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: result[k] for k in result if k != "groups"}, ensure_ascii=False, indent=2))
    print(json.dumps([{"ids": r["ids"], "true_duplicate_signature": r["true_duplicate_signature"], "same_choices": r["same_choices"], "same_answers": r["same_answers"]} for r in rows], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
