import json
from collections import Counter, defaultdict
from pathlib import Path

from knowledge_node_repair_evidence import (
    DIFFERENT_QUESTION_STRONG,
    classify_repair_confirmation,
)
from reports.question_bank_q2000_final_quality_audit import norm_text
from scripts.audit_question_content_quality import audit_question_range


ROOT = Path(__file__).resolve().parents[1]
BANK = ROOT / "licensetown" / "pt" / "data" / "question_bank"


def _read(name):
    return json.loads((BANK / name).read_text(encoding="utf-8-sig"))


def test_q2233_expansion_contract_and_distribution():
    manifest = _read("bank_manifest.json")
    assert manifest == {
        "bank_version": "2026-09-b21",
        "first_question_number": 1,
        "last_question_number": 2233,
        "question_count": 2233,
    }
    questions = _read("questions.json")
    tags = _read("question_tags.json")
    added_questions = [row for row in questions if int(row["id"][1:]) >= 2001]
    added_tags = [row for row in tags if int(row["id"][1:]) >= 2001]
    assert len(added_questions) == len(added_tags) == 233
    assert all(row["source"] == "O" for row in added_questions)
    assert all(row["source"] == "original" for row in added_tags)
    assert Counter(row["category_small"] for row in added_questions) == {
        1: 4,
        2: 8,
        6: 2,
        8: 18,
        9: 20,
        11: 3,
        13: 1,
        15: 6,
        16: 3,
        17: 54,
        18: 114,
    }


def test_q2233_added_range_passes_content_quality_fail_gate():
    report = audit_question_range(2001, 2233)
    assert report["question_count"] == 233
    assert report["fail_count"] == 0, report["findings"]


def test_every_added_question_has_preexisting_strong_same_node_reference():
    tags = _read("question_tags.json")
    by_node = defaultdict(list)
    for row in tags:
        by_node[row["knowledge_node_id"]].append(row["id"])

    missing = []
    for row in tags:
        qid = row["id"]
        if int(qid[1:]) < 2001:
            continue
        older = [candidate for candidate in by_node[row["knowledge_node_id"]] if int(candidate[1:]) <= 2000]
        if not any(
            classify_repair_confirmation(candidate, qid) == DIFFERENT_QUESTION_STRONG
            for candidate in older
        ):
            missing.append((qid, row["knowledge_node_id"], older))
    assert missing == []


def test_added_stems_are_not_exact_duplicates_of_q1_q2000():
    questions = _read("questions.json")
    old = {norm_text(row["question_text"]) for row in questions if int(row["id"][1:]) <= 2000}
    duplicates = [
        row["id"]
        for row in questions
        if int(row["id"][1:]) >= 2001 and norm_text(row["question_text"]) in old
    ]
    assert duplicates == []
