import hashlib
import json
from pathlib import Path

from knowledge_node_canonical import canonicalize_knowledge_node_id
from knowledge_node_repair_evidence import (
    DIFFERENT_QUESTION_STRONG,
    DIFFERENT_QUESTION_WEAK,
    classify_repair_confirmation,
)
from question_bank import get_answer, get_explanation, get_question, get_question_tag


ITEMS = {
    "Q1611": ("KN1399", ("Q1424",), "finding_interpretation", "INTERPRET", "B"),
    "Q1612": ("KN1151", ("Q1164", "Q1221"), "finding_interpretation", "INTERPRET", "D"),
    "Q1613": ("KN1256", ("Q1272",), "finding_interpretation", "INTERPRET", "B"),
    "Q1614": ("KN1263", ("Q1279",), "intervention_selection", "PRESCRIBE", "A"),
    "Q1615": ("KN0607", ("Q615",), "assessment_selection", "MEASURE", "A"),
}
BANK = Path(__file__).resolve().parents[1] / "data" / "question_bank"
HISTORICAL_DIGESTS = {
    "questions.json": "a7508c8f4861938ea6b166a0bb1c274a579e695d201d1b708f46b317ba0a12c4",
    "answers.json": "5febb50afe77357ded9922fc86038af2658606da28a07a9e4448cc17f786eb2b",
    "explanations.json": "1f13afeb2c42006a40df3c56a17222a6d4ee6af0f7184d8e7915bb1481ffdb2f",
    "question_tags.json": "7b0c107edf2bd20d2a0efacc628e754fc34e5866831128d56e10f2f98c9b38e3",
}


def test_q1_through_q1610_content_is_unchanged():
    for filename, expected in HISTORICAL_DIGESTS.items():
        records = json.loads((BANK / filename).read_text(encoding="utf-8-sig"))
        historical = json.dumps(
            records[:1610], ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode()
        assert hashlib.sha256(historical).hexdigest() == expected


def test_batch2_records_match_approved_design_contract():
    for q_id, (node, _sources, task, ability, key) in ITEMS.items():
        question = get_question(q_id)
        answer = get_answer(q_id)
        explanation = get_explanation(q_id)
        tag = get_question_tag(q_id)
        assert question["source"] == "O" and question["exam"] is None
        assert question["management_code"].endswith("-O")
        assert len(question["choices"]) == 5
        assert answer["display_answer"] == key
        assert answer["accepted_answer_sets"] == [[key]]
        assert answer["answer_basis"] == "LT_original"
        assert set(explanation["choice_explanations"]) == set(question["choices"])
        assert tag["knowledge_node_id"] == node
        assert tag["task"] == task and tag["primary_ability"] == ability
        assert tag["tag_status"] == "reviewed" and tag["source"] == "original"


def test_each_batch2_item_is_strong_against_every_active_wrong_source():
    for q_id, (_node, sources, _task, _ability, _key) in ITEMS.items():
        for source_q in sources:
            assert classify_repair_confirmation(source_q, q_id) == DIFFERENT_QUESTION_STRONG
            assert classify_repair_confirmation(q_id, source_q) == DIFFERENT_QUESTION_STRONG


def test_kn1256_new_interpretation_is_strong_without_changing_old_weak_policy():
    old = canonicalize_knowledge_node_id(get_question_tag("Q1272")["knowledge_node_id"])
    legacy = canonicalize_knowledge_node_id(get_question_tag("Q1457")["knowledge_node_id"])
    new = canonicalize_knowledge_node_id(get_question_tag("Q1613")["knowledge_node_id"])
    assert old == legacy == new == "KN1256"
    assert classify_repair_confirmation("Q1272", "Q1457") == DIFFERENT_QUESTION_WEAK
    assert classify_repair_confirmation("Q1272", "Q1613") == DIFFERENT_QUESTION_STRONG
    assert classify_repair_confirmation("Q1457", "Q1613") == DIFFERENT_QUESTION_STRONG


def test_gravity_line_and_tenodesis_safety_wording_is_preserved():
    assert "身体重心から鉛直に下ろした重力線" in get_question("Q1611")["question_text"]
    assert "足関節中心（外果付近）より後方" in get_question("Q1613")["question_text"]
    tenodesis = get_explanation("Q1614")["explanation"]
    assert "能動的に伸展" in tenodesis and "受動張力" in tenodesis
    assert "過度に伸張" in tenodesis and "避ける" in tenodesis
