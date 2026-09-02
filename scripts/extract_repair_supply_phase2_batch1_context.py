import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QB = ROOT / "data" / "question_bank"
TARGETS = ["Q195", "Q1599", "Q684", "Q1602", "Q25", "Q1596", "Q331", "Q1600", "Q705", "Q1603"]
FILES = {
    "questions": QB / "questions.json",
    "answers": QB / "answers.json",
    "explanations": QB / "explanations.json",
    "tags": QB / "question_tags.json",
}


def load_records(path):
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, list):
        raise SystemExit(f"expected list: {path}")
    return {str(item.get("id") or item.get("question_id")): item for item in data if isinstance(item, dict)}


stores = {name: load_records(path) for name, path in FILES.items()}
strong_pairs_path = QB / "strong_different_question_pairs.json"
strong_pairs = json.loads(strong_pairs_path.read_text(encoding="utf-8-sig"))

result = {"targets": []}
for qid in TARGETS:
    row = {"question_id": qid}
    for name, store in stores.items():
        row[name] = store.get(qid)
    tag = row.get("tags") or {}
    row["demand_pair"] = {
        "task": tag.get("task"),
        "primary_ability": tag.get("primary_ability"),
        "knowledge_node_id": tag.get("knowledge_node_id"),
        "safety": tag.get("safety"),
        "category_small": tag.get("category_small"),
    }
    result["targets"].append(row)

result["reviewed_strong_pairs_touching_targets"] = [
    item for item in strong_pairs
    if isinstance(item, dict)
    and any(str(q) in TARGETS for q in (item.get("question_ids") or []))
]

out = ROOT / "docs" / "repair-supply-phase2-batch1-source-context.json"
out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(out)
