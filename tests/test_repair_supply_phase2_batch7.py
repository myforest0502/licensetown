import hashlib
import json
from pathlib import Path

from knowledge_node_repair_evidence import (
    DIFFERENT_QUESTION_STRONG,
    classify_repair_confirmation,
)
from question_bank import (
    get_answer,
    get_explanation,
    get_question,
    get_question_tag,
    question_count,
)


ITEMS = {
    "Q1636": ("KN1100", "Q1111", "A", "B", 8),
    "Q1637": ("KN1143", "Q1156", "A", "C", 13),
    "Q1638": ("KN1149", "Q1162", "A", "A", 1),
    "Q1639": ("KN1265", "Q1281", "A", "A", 4),
    "Q1640": ("KN1321", "Q1341", "A", "C", 13),
}
BANK = Path(__file__).resolve().parents[1] / "data" / "question_bank"
HISTORICAL_DIGESTS = {
    "questions.json": "ce9331a62dbd573f5740eccf3b8aa408e15b4f598b274168f311ca9d4424e1ce",
    "answers.json": "2ed1a3cbca0c7f1354a41153fb3780177357ad88dacd7ba1f9ce4e4a9eb4373e",
    "explanations.json": "b00f0c5be2faf2afb534e4c26da4b0cf0e534342069e04e2874470457a87b4e4",
    "question_tags.json": "3a2cb2675715c894067192c09b9a99256eeca26d598019bddf8513316ad1b6e5",
}


def test_q1_through_q1635_content_is_unchanged():
    for filename, expected in HISTORICAL_DIGESTS.items():
        records = json.loads((BANK / filename).read_text(encoding="utf-8-sig"))
        historical = json.dumps(
            records[:1635], ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode()
        assert hashlib.sha256(historical).hexdigest() == expected


def test_batch7_records_match_v02_design_and_source_contracts():
    assert question_count() == 1650
    for q_id, (node, source_q, key, category, category_small) in ITEMS.items():
        question = get_question(q_id)
        source = get_question(source_q)
        answer = get_answer(q_id)
        explanation = get_explanation(q_id)
        tag = get_question_tag(q_id)
        source_tag = get_question_tag(source_q)

        assert question["source"] == "O" and question["exam"] is None
        assert question["category_large"] == source["category_large"] == category
        assert question["category_small"] == source["category_small"] == category_small
        assert question["management_code"] == f"{q_id}-{category}-{category_small}-O"
        assert len(question["choices"]) == 5
        assert answer["display_answer"] == key
        assert answer["accepted_answer_sets"] == [[key]]
        assert answer["answer_basis"] == "LT_original"
        assert set(explanation["choice_explanations"]) == set(question["choices"])
        assert tag["knowledge_node_id"] == node
        assert tag["task"] == "finding_interpretation"
        assert tag["primary_ability"] == "INTERPRET"
        assert tag["safety"] == source_tag["safety"] == "none"
        assert tag["tag_status"] == "reviewed" and tag["source"] == "original"


def test_each_batch7_item_is_strong_against_its_active_wrong_source():
    for q_id, (_node, source_q, *_rest) in ITEMS.items():
        assert classify_repair_confirmation(source_q, q_id) == DIFFERENT_QUESTION_STRONG
        assert classify_repair_confirmation(q_id, source_q) == DIFFERENT_QUESTION_STRONG


def test_q1111_and_q1281_official_answer_contracts_are_unchanged():
    assert get_answer("Q1111")["accepted_answer_sets"] == [["1"], ["2"]]
    assert get_answer("Q1111")["answer_basis"] == "MHLW_official"
    assert get_answer("Q1281")["accepted_answer_sets"] == [["3", "5"]]
    assert get_answer("Q1281")["answer_basis"] == "MHLW_official"


def test_v02_content_safeguards_are_preserved():
    medication = get_explanation("Q1636")["explanation"]
    assert "持ち越し" in medication and "自己判断せず" in medication
    scapula = get_explanation("Q1637")["explanation"]
    assert "力のカップル" in scapula and "単独" in scapula
    embolism = get_explanation("Q1638")["explanation"]
    assert "右房、右室" in embolism and "肺動脈" in embolism
    development = get_explanation("Q1639")["explanation"]
    assert "12か月以前" in development and "発達遅滞を確定しない" in development
    adaptation = get_explanation("Q1640")["explanation"]
    assert "予測誤差" in adaptation and "after-effect" in adaptation
