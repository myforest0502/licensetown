import copy
import json
from pathlib import Path

from scripts.integrate_question_bank_q2000_final_past_exam import ITEMS, integrate

ROOT = Path(__file__).resolve().parents[1]
BANK = ROOT / "data" / "question_bank"


def read(name):
    return json.loads((BANK / name).read_text(encoding="utf-8-sig"))


def test_final_six_are_source_verified_and_aligned():
    questions = {row["id"]: row for row in read("questions.json")}
    answers = {row["id"]: row for row in read("answers.json")}
    tags = {row["id"]: row for row in read("question_tags.json")}
    audit = read("question_bank_q2000_final_past_exam_source_audit.json")
    assert [row["id"] for row in audit["items"]] == [row["id"] for row in ITEMS]
    for item in ITEMS:
        qid = item["id"]
        assert questions[qid]["exam"] == {"exam_no": 60, "session": "午後", "question_no": item["question_no"]}
        assert answers[qid]["accepted_answer_sets"] == [item["answers"]]
        assert answers[qid]["answer_basis"] == "MHLW_official"
        assert tags[qid]["knowledge_node_id"] == item["node_id"]
        assert tags[qid]["source"] == "past_exam"


def test_final_bank_contract_and_new_node_membership():
    manifest = read("bank_manifest.json")
    nodes = {row["knowledge_node_id"]: row for row in read("knowledge_nodes.json")}
    assert manifest == {"bank_version": "2026-09-b20", "first_question_number": 1, "last_question_number": 2000, "question_count": 2000}
    for node_id, qid in (("KN1559", "Q1995"), ("KN1560", "Q1996"), ("KN1561", "Q1997"), ("KN1562", "Q1998")):
        assert nodes[node_id]["question_ids"] == [qid]
        assert nodes[node_id]["status"] == "singleton_initial"
    assert nodes["KN0307"]["question_ids"][-1] == "Q1999"
    assert nodes["KN0600"]["question_ids"][-1] == "Q2000"


def test_integration_is_idempotent(tmp_path):
    target = tmp_path / "bank"
    target.mkdir()
    for rel in ("questions.json", "answers.json", "explanations.json", "question_tags.json", "knowledge_nodes.json", "bank_manifest.json", "schema/question_bank_schema_v1.json"):
        src, dst = BANK / rel, target / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(src.read_bytes())
    before = {p.relative_to(target): p.read_bytes() for p in target.rglob("*.json")}
    integrate(target)
    after = {p.relative_to(target): p.read_bytes() for p in target.rglob("*.json")}
    assert after == before


def test_q1_q1994_content_is_unchanged_by_contract():
    for name in ("questions.json", "answers.json", "explanations.json", "question_tags.json"):
        rows = read(name)
        assert [row["id"] for row in rows[:1994]] == [f"Q{i}" for i in range(1, 1995)]
