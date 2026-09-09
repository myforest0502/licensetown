import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BANK = ROOT / "data" / "question_bank"


def _load(name):
    return json.loads((BANK / name).read_text(encoding="utf-8-sig"))


def test_q2000_node_label_probe():
    questions = {r["id"]: r for r in _load("questions.json")}
    answers = {r["id"]: r for r in _load("answers.json")}
    explanations = {r["id"]: r for r in _load("explanations.json")}
    tags = {r["id"]: r for r in _load("question_tags.json")}
    nodes = {r["knowledge_node_id"]: r for r in _load("knowledge_nodes.json")}
    ids = ["Q605", "Q815", "Q1960", "Q1155", "Q1268"]

    def detail(qid):
        q = questions[qid]
        a = answers[qid]
        e = explanations[qid]
        t = tags[qid]
        return {
            "id": qid,
            "stem": q.get("question_text") or q.get("question") or q.get("stem"),
            "choices": q.get("choices") or q.get("options"),
            "answer": a.get("accepted_answer_sets") or a.get("display_answer") or a.get("answer") or a.get("correct_answer"),
            "explanation": e.get("explanation"),
            "choice_explanations": e.get("choice_explanations"),
            "tag": t,
        }

    print("Q2000_NODE_LABEL_DETAIL=" + json.dumps({
        "nodes": [nodes[x] for x in ["KN0597", "KN0807", "KN1142", "KN1252"]],
        "questions": [detail(qid) for qid in ids],
    }, ensure_ascii=False, sort_keys=True))
    assert False, "intentional diagnostic probe"
