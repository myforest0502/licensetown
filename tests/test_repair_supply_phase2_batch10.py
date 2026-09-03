import hashlib
import json
from pathlib import Path

from knowledge_node_canonical import canonicalize_knowledge_node_id
from knowledge_node_repair_evidence import DIFFERENT_QUESTION_STRONG, classify_repair_confirmation
from question_bank import get_answer, get_explanation, get_question, get_question_tag, question_count


ITEMS = {
    "Q1651": ("KN0966", "Q976", "B", "B", 8, "assessment_selection", "MEASURE", "INTERPRET"),
    "Q1652": ("KN0988", "Q998", "C", "C", 15, "finding_interpretation", "INTERPRET", "KNOW"),
    "Q1653": ("KN1029", "Q1039", "B", "A", 3, "finding_interpretation", "INTERPRET", "KNOW"),
    "Q1654": ("KN1470", "Q1495", "D", "A", 3, "finding_interpretation", "INTERPRET", "MEASURE"),
    "Q1655": ("KN1475", "Q1500", "A", "B", 8, "finding_interpretation", "INTERPRET", "KNOW"),
}
BANK = Path(__file__).resolve().parents[1] / "data" / "question_bank"
HISTORICAL_DIGESTS = {
    "questions.json": "f9587737f962b33df4ac4d936e8e4bb0e683aeb790f8403ba1a7acee4b104319",
    "answers.json": "9ef9e7de28ba9c230c1c34eef28d16985b9076ba5d83b3cdb7b407de532ac551",
    "explanations.json": "1eebe8e81b056859df2404d5ff45a802fb0ffe8c365ab8964408136579468baf",
    "question_tags.json": "52adbff1c8b4500016c30122d19f9d2c81e742d2354746822ea2d17ec8b92af7",
}


def test_q1_through_q1650_content_is_unchanged():
    for filename, expected in HISTORICAL_DIGESTS.items():
        records = json.loads((BANK / filename).read_text(encoding="utf-8-sig"))
        historical = json.dumps(
            records[:1650], ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode()
        assert hashlib.sha256(historical).hexdigest() == expected


def test_batch10_records_match_formal_design():
    assert question_count() == 1680
    for q_id, (node, source, key, category, small, task, primary, secondary) in ITEMS.items():
        question = get_question(q_id)
        answer = get_answer(q_id)
        explanation = get_explanation(q_id)
        tag = get_question_tag(q_id)
        assert question["source"] == "O" and question["exam"] is None
        assert question["category_large"] == category and question["category_small"] == small
        assert question["management_code"] == f"{q_id}-{category}-{small}-O"
        assert answer["accepted_answer_sets"] == [[key]] and answer["answer_basis"] == "LT_original"
        assert set(explanation["choice_explanations"]) == set(question["choices"])
        assert tag["knowledge_node_id"] == node
        assert (tag["task"], tag["primary_ability"], tag["secondary_ability"]) == (task, primary, secondary)
        assert tag["safety"] == "none" and tag["source"] == "original"
        assert canonicalize_knowledge_node_id(get_question_tag(source)["knowledge_node_id"]) == node


def test_all_required_batch10_pairs_are_formally_strong_bidirectionally():
    for q_id, (_node, source, *_rest) in ITEMS.items():
        assert classify_repair_confirmation(source, q_id) == DIFFERENT_QUESTION_STRONG
        assert classify_repair_confirmation(q_id, source) == DIFFERENT_QUESTION_STRONG


def test_official_multiple_answer_contracts_are_unchanged():
    assert get_answer("Q998") == {
        "id": "Q998", "display_answer": "3・4",
        "accepted_answer_sets": [["3", "4"]], "answer_basis": "MHLW_official",
    }
    assert get_answer("Q1500") == {
        "id": "Q1500", "display_answer": "2・5",
        "accepted_answer_sets": [["2", "5"]], "answer_basis": "MHLW_official",
    }


def test_content_safeguards_are_preserved():
    ami = get_explanation("Q1651")["explanation"]
    assert "心筋壊死を直接評価" in ami and "別の理由" in ami
    assert "総腓骨神経麻痺" in get_explanation("Q1652")["explanation"]
    assert "必ずしも直線的" in get_explanation("Q1653")["explanation"]
    assert "確定診断" in get_explanation("Q1654")["explanation"]
    assert "全症例で感覚障害が必須" in get_explanation("Q1655")["explanation"]
