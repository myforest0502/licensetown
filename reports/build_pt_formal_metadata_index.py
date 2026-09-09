"""Build a compact read-only Q1-Q2000 metadata index for PT audits.

This artifact is derived only from the formal Question Bank and is not an app datastore.
"""
from __future__ import annotations

import json
from pathlib import Path

from question_bank import get_category_name, get_category_small, get_question_tag, question_ids

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "pt_formal_metadata_index.json"


def main():
    rows = {}
    for qid in question_ids():
        tag = get_question_tag(qid)
        field_id = get_category_small(qid)
        rows[qid] = {
            "field_id": field_id,
            "field_name": get_category_name(field_id),
            "knowledge_node_id": tag.get("knowledge_node_id") or tag.get("knowledge_node"),
            "task": tag.get("task"),
            "level": tag.get("level"),
            "safety": tag.get("safety"),
            "primary_ability": tag.get("primary_ability"),
            "source": tag.get("source"),
        }
    OUT.write_text(json.dumps(rows, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    print(json.dumps({"question_count": len(rows), "first": next(iter(rows)), "last": list(rows)[-1]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
