import hashlib
import itertools
import json
from pathlib import Path

from knowledge_node_canonical import canonicalize_knowledge_node_id
from knowledge_node_repair_evidence import (
    DIFFERENT_QUESTION_STRONG,
    DIFFERENT_QUESTION_WEAK,
    classify_repair_confirmation,
)
from question_bank import get_answer, get_explanation, get_question, get_question_tag, question_count


ITEMS = {
    "Q1641": ("KN1337", ("Q1358", "Q954", "Q1535"), "C", "A", 1),
    "Q1642": ("KN1494", ("Q1519",), "A", "C", 17),
    "Q1643": ("KN1514", ("Q1540",), "B", "A", 1),
    "Q1644": ("KN1080", ("Q1091", "Q1544"), "C", "C", 13),
    "Q1645": ("KN1224", ("Q1239",), "C", "C", 15),
}
BANK = Path(__file__).resolve().parents[1] / "data" / "question_bank"
HISTORICAL_DIGESTS = {
    "questions.json": "8b3f2a0b070371abf4036a1da9eb13af8d3e38ad3cb123a31811d72b9780ed85",
    "answers.json": "e366ded5242fe5dbf8b1c8e60f27d76b4cab1de6cbbbda3bcec6fa8e80c025fd",
    "explanations.json": "1ec341a191f043eb7369727d9662266dcfd6f59ad4c0c1edc85fbc7d38cbed99",
    "question_tags.json": "b85b7448e7882b669532961909be65b7868755f275c39de181211a29cbcda258",
}


def test_q1_through_q1640_content_is_unchanged():
    for filename, expected in HISTORICAL_DIGESTS.items():
        records = json.loads((BANK / filename).read_text(encoding="utf-8-sig"))
        historical = json.dumps(
            records[:1640], ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode()
        assert hashlib.sha256(historical).hexdigest() == expected


def test_batch8_records_match_v02_design_and_source_contracts():
    assert question_count() == 1737
    for q_id, (node, sources, key, category, small) in ITEMS.items():
        question = get_question(q_id)
        answer = get_answer(q_id)
        explanation = get_explanation(q_id)
        tag = get_question_tag(q_id)
        assert question["source"] == "O" and question["exam"] is None
        assert question["category_large"] == category and question["category_small"] == small
        assert question["management_code"] == f"{q_id}-{category}-{small}-O"
        assert get_question(sources[0])["category_large"] == category
        assert answer["accepted_answer_sets"] == [[key]] and answer["answer_basis"] == "LT_original"
        assert set(explanation["choice_explanations"]) == set(question["choices"])
        assert tag["knowledge_node_id"] == node
        assert tag["task"] == "finding_interpretation" and tag["primary_ability"] == "INTERPRET"
        assert tag["safety"] == "none" and tag["source"] == "original"


def test_new_items_are_strong_against_every_current_canonical_source():
    for q_id, (node, sources, *_rest) in ITEMS.items():
        for source_q in sources:
            assert canonicalize_knowledge_node_id(get_question_tag(source_q)["knowledge_node_id"]) == node
            assert classify_repair_confirmation(source_q, q_id) == DIFFERENT_QUESTION_STRONG
            assert classify_repair_confirmation(q_id, source_q) == DIFFERENT_QUESTION_STRONG


def test_existing_near_duplicate_families_remain_weak():
    for left, right in itertools.combinations(("Q1358", "Q954", "Q1535"), 2):
        assert classify_repair_confirmation(left, right) == DIFFERENT_QUESTION_WEAK
        assert classify_repair_confirmation(right, left) == DIFFERENT_QUESTION_WEAK
    assert classify_repair_confirmation("Q1091", "Q1544") == DIFFERENT_QUESTION_WEAK
    assert classify_repair_confirmation("Q1544", "Q1091") == DIFFERENT_QUESTION_WEAK


def test_official_answer_contracts_are_unchanged():
    assert get_answer("Q1519")["accepted_answer_sets"] == [["4"], ["5"]]
    assert get_answer("Q1540")["accepted_answer_sets"] == [["2"], ["4"]]
    assert get_answer("Q1239")["accepted_answer_sets"] == [["3", "4"]]
    assert all(get_answer(q_id)["answer_basis"] == "MHLW_official" for q_id in ("Q1519", "Q1540", "Q1239"))


def test_v02_content_safeguards_are_preserved():
    assert "角加速度" in get_explanation("Q1641")["explanation"]
    assert "確定診断" in get_explanation("Q1642")["explanation"]
    assert "膀胱頸部" in get_explanation("Q1643")["explanation"]
    assert "筋長が伸びる" in get_explanation("Q1644")["explanation"]
    gait = get_explanation("Q1645")["explanation"]
    assert "立脚中期から立脚終期" in gait and "両脚支持" in gait
