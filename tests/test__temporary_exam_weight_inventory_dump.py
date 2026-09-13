import json
from collections import Counter, defaultdict
from pathlib import Path

import pytest

from question_bank import CATEGORY_NAMES, get_category_small

ROOT = Path(__file__).resolve().parents[1]
QB = ROOT / "data" / "question_bank"


def _load(name):
    return json.loads((QB / name).read_text(encoding="utf-8"))


def test_emit_exam_weight_inventory_for_one_off_audit():
    tags = _load("question_tags.json")
    source_counts = Counter(row["source"] for row in tags)
    by_field = defaultdict(lambda: Counter())
    for row in tags:
        fid = get_category_small(row["id"])
        by_field[fid][row["source"]] += 1
        by_field[fid]["total"] += 1

    provenance = {}
    known_qids = set()

    strong = _load("past_exam_strong_different_q_v01_source_audit.json")
    strong_imported = [r for r in strong if str(r.get("import_status", "")).startswith("imported")]
    provenance["strong_exam_counts"] = dict(sorted(Counter(r["exam_no"] for r in strong_imported).items()))
    known_qids.update(r["new_question_id"] for r in strong_imported)

    for filename in (
        "past_exam_normal_import_47_51_v01_source_audit.json",
        "past_exam_normal_import_47_51_lot2_v01_source_audit.json",
    ):
        rows = _load(filename)
        imported = [r for r in rows if r.get("decision") == "IMPORTED"]
        exam_counts = Counter()
        for r in imported:
            source_key = str(r.get("source_key", ""))
            if source_key[:2].isdigit():
                exam_counts[int(source_key[:2])] += 1
            if r.get("new_question_id"):
                known_qids.add(r["new_question_id"])
        provenance[filename] = dict(sorted(exam_counts.items()))

    q2000 = _load("question_bank_q2000_final_past_exam_source_audit.json")
    provenance["q2000_exam"] = q2000.get("exam")
    provenance["q2000_items"] = len(q2000.get("items", []))
    known_qids.update(r["id"] for r in q2000.get("items", []))

    report = {
        "source_counts": dict(source_counts),
        "field_counts": {
            str(fid): {
                "name": CATEGORY_NAMES[fid],
                "total": by_field[fid]["total"],
                "past_exam": by_field[fid]["past_exam"],
                "original": by_field[fid]["original"],
            }
            for fid in sorted(CATEGORY_NAMES)
        },
        "year_provenance_audit": provenance,
        "known_year_provenance_qids": len(known_qids),
        "past_exam_qids": source_counts["past_exam"],
        "year_provenance_gap": source_counts["past_exam"] - len(known_qids),
    }
    pytest.fail("EXAM_WEIGHT_INVENTORY=" + json.dumps(report, ensure_ascii=False, sort_keys=True))
