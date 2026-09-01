import json
from pathlib import Path

from knowledge_node_canonical import canonicalize_knowledge_node_id
from knowledge_node_repair_evidence import (
    DIFFERENT_QUESTION_STRONG,
    DIFFERENT_QUESTION_WEAK,
    SAME_QUESTION,
    classify_repair_confirmation,
)
from question_bank import get_question_tag


PILOT_PAIRS = (
    ("Q8", "Q1595"),
    ("Q25", "Q1596"),
    ("Q36", "Q1597"),
    ("Q109", "Q1598"),
    ("Q195", "Q1599"),
    ("Q331", "Q1600"),
    ("Q379", "Q1601"),
    ("Q684", "Q1602"),
    ("Q705", "Q1603"),
    ("Q1305", "Q1604"),
    ("Q1504", "Q1605"),
)


def canonical_node(question_id):
    return canonicalize_knowledge_node_id(
        get_question_tag(question_id)["knowledge_node_id"]
    )


def test_same_question_remains_same_question():
    assert classify_repair_confirmation("Q8", "Q8") == SAME_QUESTION


def test_cross_node_questions_fail_closed_even_when_demands_differ():
    assert canonical_node("Q8") != canonical_node("Q1596")
    assert classify_repair_confirmation("Q8", "Q1596") == DIFFERENT_QUESTION_WEAK


def test_safety_strong_repair_pilot_pairs_remain_strong():
    for source_q, alternate_q in PILOT_PAIRS:
        assert canonical_node(source_q) == canonical_node(alternate_q)
        assert classify_repair_confirmation(source_q, alternate_q) == DIFFERENT_QUESTION_STRONG


def test_every_reviewed_strong_pair_stays_within_one_canonical_node():
    pair_path = (
        Path(__file__).resolve().parents[1]
        / "data"
        / "question_bank"
        / "strong_different_question_pairs.json"
    )
    records = json.loads(pair_path.read_text(encoding="utf-8-sig"))
    reviewed = [
        item for item in records
        if item.get("review_status") == "reviewed" and item.get("strength") == "strong"
    ]
    assert reviewed
    for item in reviewed:
        first, second = item["question_ids"]
        assert canonical_node(first) == canonical_node(second)
        assert canonical_node(first) == canonicalize_knowledge_node_id(item["knowledge_node_id"])
        assert classify_repair_confirmation(first, second) == DIFFERENT_QUESTION_STRONG
