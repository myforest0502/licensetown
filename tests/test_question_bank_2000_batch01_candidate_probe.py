import json
from pathlib import Path


def test_batch01_candidate_probe():
    root = Path(__file__).resolve().parents[1]
    bank = root / "data" / "question_bank"
    questions = {row["id"]: row for row in json.loads((bank / "questions.json").read_text(encoding="utf-8-sig"))}
    tags = {row["id"]: row for row in json.loads((bank / "question_tags.json").read_text(encoding="utf-8-sig"))}
    nodes = {
        row["knowledge_node_id"]: row
        for row in json.loads((bank / "knowledge_nodes.json").read_text(encoding="utf-8-sig"))
    }

    candidate_qids = ["Q406", "Q103", "Q43", "Q83", "Q102", "Q10"]
    payload = []
    for qid in candidate_qids:
        q = questions[qid]
        tag = tags[qid]
        node_id = tag["knowledge_node_id"]
        node = nodes[node_id]
        payload.append(
            {
                "qid": qid,
                "node_id": node_id,
                "node_label": node.get("canonical_label"),
                "node_status": node.get("status"),
                "node_question_ids": node.get("question_ids"),
                "category_large": q.get("category_large"),
                "category_small": q.get("category_small"),
                "question_text": q.get("question_text"),
                "choices": q.get("choices"),
                "task": tag.get("task"),
                "primary_ability": tag.get("primary_ability"),
                "secondary_ability": tag.get("secondary_ability"),
                "level": tag.get("level"),
                "safety": tag.get("safety"),
            }
        )

    raise AssertionError("BATCH01_CANDIDATE_PROBE\n" + json.dumps(payload, ensure_ascii=False, indent=2))
