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
    "Q1621": ("KN1395", "Q1420", "finding_interpretation", "INTERPRET", "C", "A", 2),
    "Q1622": ("KN0678", "Q686", "finding_interpretation", "INTERPRET", "A", "A", 3),
    "Q1623": ("KN0002", "Q2", "intervention_selection", "PRESCRIBE", "A", "C", 15),
    "Q1624": ("KN1468", "Q1493", "intervention_selection", "PRESCRIBE", "B", "B", 7),
    "Q1625": ("KN0065", "Q65", "intervention_selection", "PRESCRIBE", "B", "C", 15),
}
BANK = Path(__file__).resolve().parents[1] / "data" / "question_bank"
HISTORICAL_DIGESTS = {
    "questions.json": "728c042e9bf4c1b71b5c3e07ed84a3e9858783dc9125fca1a81a5c6731f82eff",
    "answers.json": "f38a3e1884cd1056e6572e7059fe6417aad7a91be1e7217c0e6bc1c018556089",
    "explanations.json": "42eb4fa6624b2ddbe33ff0dda3495192a33375f559384b0e923976d4a8a1c0f8",
    "question_tags.json": "2c28510d8e92d2778d4788a378e0a6ec9a7d12577492f48d77b6a28427407a32",
}


def test_q1_through_q1620_content_is_unchanged():
    for filename, expected in HISTORICAL_DIGESTS.items():
        records = json.loads((BANK / filename).read_text(encoding="utf-8-sig"))
        historical = json.dumps(
            records[:1620], ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode()
        assert hashlib.sha256(historical).hexdigest() == expected


def test_batch4_records_match_approved_v02_design_and_source_categories():
    assert question_count() == 1635
    for q_id, (node, source_q, task, ability, key, category, category_small) in ITEMS.items():
        question = get_question(q_id)
        source = get_question(source_q)
        answer = get_answer(q_id)
        explanation = get_explanation(q_id)
        tag = get_question_tag(q_id)

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
        assert tag["task"] == task and tag["primary_ability"] == ability
        assert tag["tag_status"] == "reviewed" and tag["source"] == "original"


def test_each_batch4_item_is_strong_against_its_active_wrong_source():
    for q_id, (_node, source_q, _task, _ability, _key, _category, _small) in ITEMS.items():
        assert classify_repair_confirmation(source_q, q_id) == DIFFERENT_QUESTION_STRONG
        assert classify_repair_confirmation(q_id, source_q) == DIFFERENT_QUESTION_STRONG


def test_v02_content_safeguards_are_preserved():
    motor_unit = get_explanation("Q1621")["explanation"]
    assert "その運動単位に属する筋線維" in motor_unit
    assert "筋全体のすべての筋線維ではない" in motor_unit

    aging = get_explanation("Q1622")["explanation"]
    assert "正常加齢" in aging and "個人差" in aging
    assert "認知症を診断" in aging and "断定" in aging

    valgus = get_question("Q1623")
    assert "急性の靱帯損傷は疑われない" in valgus["question_text"]
    assert "股関節外転筋・外旋筋" in valgus["choices"]["A"]
    assert "運動制御" in valgus["choices"]["A"]

    transference = get_explanation("Q1624")["explanation"]
    assert "探索し解釈" in transference and "境界" in transference
    assert "意図的に増幅" in transference

    participation = get_explanation("Q1625")["explanation"]
    assert "段階的な身体活動" in participation
    assert "本人が意味や価値" in participation
    assert "一律に押し付けず" in participation
