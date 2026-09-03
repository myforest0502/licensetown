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
    "Q1631": ("KN0811", "Q820", "finding_interpretation", "INTERPRET", "C", "A", 2),
    "Q1632": ("KN0894", "Q903", "finding_interpretation", "INTERPRET", "C", "A", 3),
    "Q1633": ("KN1044", "Q1054", "finding_interpretation", "INTERPRET", "A", "C", 13),
    "Q1634": ("KN1047", "Q1057", "finding_interpretation", "INTERPRET", "D", "C", 18),
    "Q1635": ("KN1078", "Q1089", "finding_interpretation", "INTERPRET", "C", "C", 13),
}
BANK = Path(__file__).resolve().parents[1] / "data" / "question_bank"
HISTORICAL_DIGESTS = {
    "questions.json": "b6fdc8fc7a88279b379e48eebfbe2a3c84c5b8423c24e7c0fe724baa2fc21eb0",
    "answers.json": "b5ffbdc60debe0385527fd2e457d2ec913b0e5fee667f653e03ff9fe552cf793",
    "explanations.json": "dec4dead68313d0ad3bb556d8d7cb463ed36b21aabb14c1517836818a1b171a2",
    "question_tags.json": "9fc89ef50c8f82a3067f2e601891f6943f1791254d6674dd6ff4eaf040855a59",
}


def test_q1_through_q1630_content_is_unchanged():
    for filename, expected in HISTORICAL_DIGESTS.items():
        records = json.loads((BANK / filename).read_text(encoding="utf-8-sig"))
        historical = json.dumps(
            records[:1630], ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode()
        assert hashlib.sha256(historical).hexdigest() == expected


def test_batch6_records_match_approved_v02_design_and_source_categories():
    assert question_count() == 1680
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


def test_each_batch6_item_is_strong_against_its_active_wrong_source():
    for q_id, (_node, source_q, *_rest) in ITEMS.items():
        assert classify_repair_confirmation(source_q, q_id) == DIFFERENT_QUESTION_STRONG
        assert classify_repair_confirmation(q_id, source_q) == DIFFERENT_QUESTION_STRONG


def test_q1089_official_multiple_answer_contract_is_unchanged():
    answer = get_answer("Q1089")
    assert answer["display_answer"]
    assert answer["accepted_answer_sets"] == [["3"], ["5"]]
    assert answer["answer_basis"] == "MHLW_official"


def test_v02_content_safeguards_are_preserved():
    thermoregulation = get_explanation("Q1631")["explanation"]
    assert "温度情報を統合" in thermoregulation and "末梢効果器そのものではない" in thermoregulation
    erikson = get_explanation("Q1632")["explanation"]
    assert "具体的な行動" in erikson and "年齢だけ" in erikson
    motor_learning = get_explanation("Q1633")["explanation"]
    assert "量や頻度を調整" in motor_learning and "恒久的依存" in motor_learning
    tremor = get_explanation("Q1634")["explanation"]
    assert "規則的・律動的" in tremor and "観察所見" in tremor
    radial_deviation = get_explanation("Q1635")["explanation"]
    assert "橈屈を補助" in radial_deviation and "主な手関節橈屈筋" in radial_deviation
