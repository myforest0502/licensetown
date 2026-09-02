import hashlib
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
    "Q1616": ("KN1186", ("Q1200",), "finding_interpretation", "INTERPRET", "B"),
    "Q1617": ("KN0611", ("Q619",), "finding_interpretation", "INTERPRET", "C"),
    "Q1618": ("KN0714", ("Q722",), "finding_interpretation", "INTERPRET", "B"),
    "Q1619": ("KN0725", ("Q733", "Q949"), "finding_interpretation", "INTERPRET", "A"),
    "Q1620": ("KN1281", ("Q1297",), "assessment_selection", "MEASURE", "C"),
}
BANK = Path(__file__).resolve().parents[1] / "data" / "question_bank"
HISTORICAL_DIGESTS = {
    "questions.json": "5f65e55844d7eb324d3faba583c7ce243c112d77a0032219ccb6da36be674d33",
    "answers.json": "19418642ccb8dd798af61f25ca20d19e587a79aaf5ec7aba83b2256c8c514cf6",
    "explanations.json": "b0c6181665d67ec7fee8e8cab0c4a8503f93523b65039f6c280e8b975d72a0b4",
    "question_tags.json": "322327035a19203f9971e356a556fb9b6a4850ca34cbe76fe24cf6fdd1802984",
}


def test_q1_through_q1615_content_is_unchanged():
    for filename, expected in HISTORICAL_DIGESTS.items():
        records = json.loads((BANK / filename).read_text(encoding="utf-8-sig"))
        historical = json.dumps(
            records[:1615], ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode()
        assert hashlib.sha256(historical).hexdigest() == expected


def test_batch3_records_match_approved_v02_design_contract():
    assert question_count() == 1625
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


def test_each_batch3_item_is_strong_against_every_active_wrong_source():
    for q_id, (_node, sources, _task, _ability, _key) in ITEMS.items():
        for source_q in sources:
            assert classify_repair_confirmation(source_q, q_id) == DIFFERENT_QUESTION_STRONG
            assert classify_repair_confirmation(q_id, source_q) == DIFFERENT_QUESTION_STRONG


def test_kn0725_new_interpretation_is_strong_without_changing_old_weak_policy():
    old = canonicalize_knowledge_node_id(get_question_tag("Q733")["knowledge_node_id"])
    legacy = canonicalize_knowledge_node_id(get_question_tag("Q949")["knowledge_node_id"])
    new = canonicalize_knowledge_node_id(get_question_tag("Q1619")["knowledge_node_id"])
    assert old == legacy == new == "KN0725"
    assert classify_repair_confirmation("Q733", "Q949") == DIFFERENT_QUESTION_WEAK
    assert classify_repair_confirmation("Q733", "Q1619") == DIFFERENT_QUESTION_STRONG
    assert classify_repair_confirmation("Q949", "Q1619") == DIFFERENT_QUESTION_STRONG


def test_v02_educational_independence_and_scope_wording_is_preserved():
    q1616 = get_question("Q1616")["question_text"]
    assert "筋腹は前腕" in q1616 and "腱が手関節を越えて" in q1616

    q1617 = get_question("Q1617")["question_text"]
    assert "思い出せない" in q1617 and "所要時間と誤り数" in q1617

    q1618 = get_question("Q1618")["question_text"]
    assert "他の評価所見は提示されていない" in q1618
    assert "自己申告による疼痛強度" in get_question("Q1618")["choices"]["B"]

    q1619 = get_question("Q1619")["question_text"]
    assert "内転位" in q1619 and "下方" in q1619 and "垂直方向の複視" in q1619

    q1620 = get_question("Q1620")["question_text"]
    assert "頭の中に保ちながら並べ替える" in q1620
    assert "逆順に再生" in get_question("Q1620")["choices"]["C"]
