import json
from pathlib import Path


def _load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def test_batch01_formal_shape_probe():
    root = Path(__file__).resolve().parents[1]
    bank = root / "data" / "question_bank"
    qids = ["Q10", "Q16", "Q24", "Q26", "Q27", "Q32", "Q33", "Q43", "Q83", "Q102", "Q103", "Q406", "Q1596", "Q1608", "Q1736", "Q1737"]
    node_ids = ["KN0010", "KN0016", "KN0024", "KN0026", "KN0027", "KN0032", "KN0033", "KN0043", "KN0083", "KN0102", "KN0103", "KN0400", "KN0025"]

    stores = {}
    for filename in ["questions.json", "answers.json", "explanations.json", "question_tags.json"]:
        rows = _load(bank / filename)
        index = {row["id"]: row for row in rows}
        stores[filename] = {qid: index.get(qid) for qid in qids}
        stores[filename + "__tail"] = rows[-3:]

    nodes = _load(bank / "knowledge_nodes.json")
    node_index = {row["knowledge_node_id"]: row for row in nodes}
    payload = {
        "stores": stores,
        "nodes": {node_id: node_index.get(node_id) for node_id in node_ids},
        "node_tail": nodes[-3:],
        "manifest": _load(bank / "bank_manifest.json"),
    }
    raise AssertionError("BATCH01_FORMAL_SHAPE_PROBE\n" + json.dumps(payload, ensure_ascii=False, indent=2))
