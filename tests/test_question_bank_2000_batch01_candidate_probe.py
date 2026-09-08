import json
from pathlib import Path


def test_batch01_replacement_candidates_remain_singletons():
    root = Path(__file__).resolve().parents[1]
    bank = root / "data" / "question_bank"
    tags = {row["id"]: row for row in json.loads((bank / "question_tags.json").read_text(encoding="utf-8-sig"))}
    nodes = {
        row["knowledge_node_id"]: row
        for row in json.loads((bank / "knowledge_nodes.json").read_text(encoding="utf-8-sig"))
    }

    expected = {
        "Q406": "KN0400",
        "Q103": "KN0103",
        "Q43": "KN0043",
        "Q83": "KN0083",
        "Q102": "KN0102",
        "Q10": "KN0010",
    }
    for qid, node_id in expected.items():
        assert tags[qid]["knowledge_node_id"] == node_id
        assert nodes[node_id]["status"] == "singleton_initial"
        assert nodes[node_id]["question_ids"] == [qid]
