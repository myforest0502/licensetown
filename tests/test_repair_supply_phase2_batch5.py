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
from question_bank import (
    get_answer,
    get_explanation,
    get_question,
    get_question_tag,
    question_count,
)


ITEMS = {
    "Q1626": ("KN0404", ("Q410",), "finding_interpretation", "INTERPRET", "B", "A", 4),
    "Q1627": ("KN0412", ("Q1580", "Q419"), "intervention_selection", "PRESCRIBE", "B", "C", 18),
    "Q1628": ("KN0483", ("Q491",), "finding_interpretation", "INTERPRET", "B", "A", 4),
    "Q1629": ("KN0609", ("Q617", "Q1225", "Q1363"), "finding_interpretation", "INTERPRET", "A", "B", 7),
    "Q1630": ("KN0799", ("Q807",), "finding_interpretation", "INTERPRET", "D", "A", 1),
}
BANK = Path(__file__).resolve().parents[1] / "data" / "question_bank"
HISTORICAL_DIGESTS = {
    "questions.json": "4b44153b23a7b7f6d9d75d9eb1699793aa73d6d1fded68395a7dcc7d36b98568",
    "answers.json": "c2d63463c19c962c7488be867348bcb484c691a73b49c16646c12ad0a26e777e",
    "explanations.json": "317647c5f685ca4af44138e8e8876968b84105947b61b394d4afd86b9ba2b241",
    "question_tags.json": "6131413467d47b4e172523728add3038c23d2a53014d7504ee53284a2a7bde7e",
}


def test_q1_through_q1625_content_is_unchanged():
    for filename, expected in HISTORICAL_DIGESTS.items():
        records = json.loads((BANK / filename).read_text(encoding="utf-8-sig"))
        historical = json.dumps(
            records[:1625], ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode()
        assert hashlib.sha256(historical).hexdigest() == expected


def test_batch5_records_match_approved_v02_design_and_source_categories():
    assert question_count() == 1650
    for q_id, (node, source_ids, task, ability, key, category, category_small) in ITEMS.items():
        question = get_question(q_id)
        answer = get_answer(q_id)
        explanation = get_explanation(q_id)
        tag = get_question_tag(q_id)

        assert question["source"] == "O" and question["exam"] is None
        assert question["category_large"] == category
        assert question["category_small"] == category_small
        assert question["management_code"] == f"{q_id}-{category}-{category_small}-O"
        # Management category follows the active-wrong source. Canonicalized
        # weak candidates may predate the current category contract.
        assert get_question(source_ids[0])["category_large"] == category
        assert len(question["choices"]) == 5
        assert answer["display_answer"] == key
        assert answer["accepted_answer_sets"] == [[key]]
        assert answer["answer_basis"] == "LT_original"
        assert set(explanation["choice_explanations"]) == set(question["choices"])
        assert tag["knowledge_node_id"] == node
        assert tag["task"] == task and tag["primary_ability"] == ability
        assert tag["tag_status"] == "reviewed" and tag["source"] == "original"


def test_each_batch5_item_is_strong_against_all_approved_sources():
    for q_id, (_node, source_ids, *_rest) in ITEMS.items():
        for source_q in source_ids:
            assert classify_repair_confirmation(source_q, q_id) == DIFFERENT_QUESTION_STRONG
            assert classify_repair_confirmation(q_id, source_q) == DIFFERENT_QUESTION_STRONG


def test_existing_weak_pairs_remain_weak_without_reviewed_override():
    assert classify_repair_confirmation("Q419", "Q1580") == DIFFERENT_QUESTION_WEAK
    warfarin_questions = ("Q617", "Q1225", "Q1363")
    assert {
        canonicalize_knowledge_node_id(get_question_tag(q_id)["knowledge_node_id"])
        for q_id in warfarin_questions
    } == {"KN0609"}
    for left, right in itertools.combinations(warfarin_questions, 2):
        assert classify_repair_confirmation(left, right) == DIFFERENT_QUESTION_WEAK
        assert classify_repair_confirmation(right, left) == DIFFERENT_QUESTION_WEAK


def test_v02_content_safeguards_are_preserved():
    stnr = get_explanation("Q1626")["explanation"]
    assert "四つ這い位" in stnr and "STNR" in stnr
    spirometry = get_explanation("Q1627")["explanation"]
    assert "ゆっくり深い吸気" in spirometry and "術後無気肺" in spirometry
    corrected_age = get_explanation("Q1628")["explanation"]
    assert "修正月齢" in corrected_age and "発達遅滞と断定しない" in corrected_age
    warfarin = get_explanation("Q1629")["explanation"]
    assert "PT-INR" in warfarin and "摂取量の急変" in warfarin
    assert "納豆" in get_question("Q1629")["question_text"]
    anatomy = get_explanation("Q1630")["explanation"]
    assert "屈筋支帯" in anatomy and "豆状骨" in anatomy
