import hashlib
import json
from pathlib import Path

from knowledge_node_canonical import canonicalize_knowledge_node_id
from knowledge_node_repair_evidence import DIFFERENT_QUESTION_STRONG, classify_repair_confirmation
from question_bank import get_answer, get_explanation, get_question, get_question_tag, question_count


ITEMS = {
    "Q1656": ("KN1523", "Q1549", "D", "B", 7, "finding_interpretation", "INTERPRET", "KNOW"),
    "Q1657": ("KN1525", "Q1551", "B", "B", 10, "assessment_selection", "MEASURE", "INTERPRET"),
    "Q1658": ("KN0001", "Q1", "C", "C", 15, "assessment_selection", "MEASURE", "INTERPRET"),
    "Q1659": ("KN0072", "Q72", "A", "C", 15, "finding_interpretation", "INTERPRET", "MEASURE"),
    "Q1660": ("KN0198", "Q199", "E", "C", 15, "finding_interpretation", "INTERPRET", "MEASURE"),
}
BANK = Path(__file__).resolve().parents[1] / "data" / "question_bank"
HISTORICAL_DIGESTS = {
    "questions.json": "60572f7eb863adb6b853677fd84910431095ca38f45124ddf6b6334ed787b894",
    "answers.json": "b8cd97883093af562a2b921e2bf16bcd5625ee62ca5e6007dd0e5cafa78ac771",
    "explanations.json": "84eb7697d81f2e34ef300e16ff576f790fe1adb58c82d0cb4ad468d6aed39168",
    "question_tags.json": "76f3d865eee0180087e2154fbe875b329d949ff3e12625d924461f47d14077c7",
}


def test_q1_through_q1655_content_is_unchanged():
    for filename, expected in HISTORICAL_DIGESTS.items():
        records = json.loads((BANK / filename).read_text(encoding="utf-8-sig"))
        historical = json.dumps(
            records[:1655], ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode()
        assert hashlib.sha256(historical).hexdigest() == expected


def test_batch11_records_match_formal_design():
    assert question_count() == 1660
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


def test_all_required_batch11_pairs_are_formally_strong_bidirectionally():
    for q_id, (_node, source, *_rest) in ITEMS.items():
        assert classify_repair_confirmation(source, q_id) == DIFFERENT_QUESTION_STRONG
        assert classify_repair_confirmation(q_id, source) == DIFFERENT_QUESTION_STRONG


def test_content_safeguards_are_preserved():
    assert "すべての病期" in get_explanation("Q1656")["explanation"]
    assert "健康への不安だけで妄想と診断せず" in get_explanation("Q1657")["explanation"]
    assert "孤立した筋力を直接測定" in get_explanation("Q1658")["explanation"]
    assert "構造的破綻" in get_explanation("Q1659")["explanation"]
    pressure = get_explanation("Q1660")["explanation"]
    assert "疼痛原因の確定" in pressure and "可動域の改善" in pressure
