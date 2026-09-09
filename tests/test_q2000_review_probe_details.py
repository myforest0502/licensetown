import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BANK = ROOT / "data" / "question_bank"


def _load(name):
    return json.loads((BANK / name).read_text(encoding="utf-8-sig"))


def test_q2000_review_probe_details():
    questions = {r["id"]: r for r in _load("questions.json")}
    answers = {r["id"]: r for r in _load("answers.json")}
    explanations = {r["id"]: r for r in _load("explanations.json")}
    tags = {r["id"]: r for r in _load("question_tags.json")}
    nodes = {r["knowledge_node_id"]: r for r in _load("knowledge_nodes.json")}

    pairs = [
        ("Q1306", "Q855"), ("Q949", "Q734"), ("Q1575", "Q694"),
        ("Q688", "Q1098"), ("Q517", "Q1192"), ("Q936", "Q1192"),
        ("Q1540", "Q891"), ("Q553", "Q611"), ("Q1489", "Q1392"),
        ("Q750", "Q616"),
    ]
    editorial_ids = ["Q546", "Q934", "Q1166", "Q1171", "Q1188", "Q1200", "Q1201", "Q1216", "Q1255", "Q1428", "Q1477", "Q1495", "Q1503", "Q2000", "Q1434", "Q1532", "Q1576"]
    duplicate_node_ids = ["KN0597", "KN0807", "KN1142", "KN1252"]

    def qdetail(qid):
        q = questions[qid]
        t = tags[qid]
        a = answers[qid]
        e = explanations[qid]
        return {
            "id": qid,
            "stem": q.get("question_text") or q.get("question") or q.get("stem"),
            "choices": q.get("choices") or q.get("options"),
            "answer": a.get("accepted_answer_sets") or a.get("display_answer") or a.get("answer") or a.get("correct_answer"),
            "source": t.get("source"),
            "task": t.get("task"),
            "primary_ability": t.get("primary_ability"),
            "level": t.get("level"),
            "safety": t.get("safety"),
            "knowledge_node_id": t.get("knowledge_node_id"),
            "explanation": e.get("explanation"),
            "choice_explanations": e.get("choice_explanations"),
        }

    report = {
        "near_pairs": [[qdetail(a), qdetail(b)] for a, b in pairs],
        "editorial": [qdetail(qid) for qid in editorial_ids],
        "duplicate_nodes": [nodes[nid] for nid in duplicate_node_ids],
    }
    print("Q2000_REVIEW_DETAIL=" + json.dumps(report, ensure_ascii=False, sort_keys=True))
    assert False, "intentional diagnostic probe"
