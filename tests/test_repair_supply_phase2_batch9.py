import hashlib
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
    "Q1646": ("KN1151", ("Q1164", "Q1221", "Q1612"), "E", "A", 3, "assessment_selection", "MEASURE", "INTERPRET"),
    "Q1647": ("KN0067", ("Q67", "Q1567"), "B", "C", 15, "finding_interpretation", "INTERPRET", "MEASURE"),
    "Q1648": ("KN0534", ("Q542", "Q1591"), "C", "A", 1, "finding_interpretation", "INTERPRET", "KNOW"),
    "Q1649": ("KN0652", ("Q660", "Q1308"), "D", "C", 18, "finding_interpretation", "INTERPRET", "MEASURE"),
    "Q1650": ("KN0545", ("Q553",), "A", "C", 13, "finding_interpretation", "INTERPRET", "KNOW"),
}
BANK = Path(__file__).resolve().parents[1] / "data" / "question_bank"
HISTORICAL_DIGESTS = {
    "questions.json": "14992b600c750547c18de40942b23ae513aecb24cc427d4e8e558e6f2a0b395d",
    "answers.json": "eef98580ed4ccc0b3f9ed10eed294e082d81d4ad36ea9fe9568cfd4f8552aaac",
    "explanations.json": "b8e303c542d1647cced01398c1dc7a92c06dd668ac36ca4e6dcc23a9908251e1",
    "question_tags.json": "d74d466b6660cec18b8de0792e97fd7f4b8b6dad279e5f46b012b09daad8e978",
}


def test_q1_through_q1645_content_is_unchanged():
    for filename, expected in HISTORICAL_DIGESTS.items():
        records = json.loads((BANK / filename).read_text(encoding="utf-8-sig"))
        historical = json.dumps(
            records[:1645], ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode()
        assert hashlib.sha256(historical).hexdigest() == expected


def test_batch9_records_match_v03_and_v02_design_contracts():
    assert question_count() == 1720
    for q_id, (node, sources, key, category, small, task, primary, secondary) in ITEMS.items():
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
        assert all(canonicalize_knowledge_node_id(get_question_tag(source)["knowledge_node_id"]) == node for source in sources)


def test_every_required_batch9_pair_is_formally_strong_bidirectionally():
    for q_id, (_node, sources, *_rest) in ITEMS.items():
        for source in sources:
            assert classify_repair_confirmation(source, q_id) == DIFFERENT_QUESTION_STRONG
            assert classify_repair_confirmation(q_id, source) == DIFFERENT_QUESTION_STRONG


def test_existing_pair_semantics_are_unchanged():
    expected = {
        ("Q1164", "Q1221"): DIFFERENT_QUESTION_WEAK,
        ("Q1164", "Q1612"): DIFFERENT_QUESTION_STRONG,
        ("Q1221", "Q1612"): DIFFERENT_QUESTION_STRONG,
        ("Q67", "Q1567"): DIFFERENT_QUESTION_STRONG,
        ("Q542", "Q1591"): DIFFERENT_QUESTION_WEAK,
        ("Q660", "Q1308"): DIFFERENT_QUESTION_STRONG,
    }
    for (left, right), strength in expected.items():
        assert classify_repair_confirmation(left, right) == strength
        assert classify_repair_confirmation(right, left) == strength


def test_q660_official_multiple_answer_contract_is_unchanged():
    assert get_answer("Q660") == {
        "id": "Q660",
        "display_answer": "1・3",
        "accepted_answer_sets": [["1", "3"]],
        "answer_basis": "MHLW_official",
    }


def test_v03_and_v02_content_safeguards_are_preserved():
    q1646 = get_question("Q1646")
    assert "追加で確認する面接所見" in q1646["question_text"]
    assert "今後の生活像を自分の言葉で語れる" in q1646["choices"]["E"]
    assert "必ずしも直線的" in get_explanation("Q1646")["explanation"]
    assert "Trendelenburg徴候は陰性" in get_question("Q1647")["question_text"]
    assert "瞳孔括約筋" in get_explanation("Q1648")["explanation"]
    assert "3項目以上" in get_explanation("Q1649")["explanation"]
    assert "鵞足" in get_explanation("Q1650")["explanation"]
