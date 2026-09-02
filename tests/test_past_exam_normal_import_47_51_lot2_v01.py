import json
from pathlib import Path

from question_bank import (
    get_answer,
    get_explanation,
    get_question,
    get_question_tag,
    question_count,
)


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "question_bank"

EXPECTED = {
    "Q1592": (51, "午前", 30, "3", "KN0695", "KN0902", True, 8),
    "Q1593": (49, "午後", 33, "3", "KN0039", "KN0039", False, 11),
    "Q1594": (50, "午前", 68, "1", "KN0533", "KN0533", False, 2),
}


def _load(name):
    return json.loads((DATA / name).read_text(encoding="utf-8-sig"))


def test_lot2_imports_keep_official_answers_and_reviewed_nodes():
    assert question_count() == 1645
    for question_id, (exam_no, session, question_no, answer, _, final_node, _, category) in EXPECTED.items():
        question = get_question(question_id)
        assert question["source"] == "P"
        assert question["exam"] == {"exam_no": exam_no, "session": session, "question_no": question_no}
        assert question["category_small"] == category
        assert get_answer(question_id)["accepted_answer_sets"] == [[answer]]
        assert get_answer(question_id)["display_answer"] == answer
        assert len(get_explanation(question_id)["choice_explanations"]) == 5
        tag = get_question_tag(question_id)
        assert tag["knowledge_node_id"] == final_node
        assert tag["tag_version"] == "1.0"
        assert tag["tag_status"] == "reviewed"
        assert tag["source"] == "past_exam"


def test_lot2_source_audit_covers_all_17_input_rows_and_node_decisions():
    audit = _load("past_exam_normal_import_47_51_lot2_v01_source_audit.json")
    assert len(audit) == 17
    assert [row["input_row"] for row in audit] == list(range(1, 18))
    assert sum(row["decision"] == "IMPORTED" for row in audit) == 3
    assert sum(row["decision"] == "HOLD" for row in audit) == 9
    assert sum(row["decision"] == "EXCLUDED_DUPLICATE" for row in audit) == 2
    assert sum(row["decision"] == "EXCLUDED_EXTRACTION_QUALITY" for row in audit) == 2
    assert sum(row["decision"] == "EXCLUDED_DUPLICATE_INPUT_ROW" for row in audit) == 1

    imported = {row["new_question_id"]: row for row in audit if row["decision"] == "IMPORTED"}
    for question_id, (_, _, _, _, original_node, final_node, changed, _) in EXPECTED.items():
        assert imported[question_id]["original_candidate_node"] == original_node
        assert imported[question_id]["final_node"] == final_node
        assert imported[question_id]["node_changed"] is changed


def test_lot2_duplicate_and_extraction_holds_are_explicit():
    audit = _load("past_exam_normal_import_47_51_lot2_v01_source_audit.json")
    by_source = {}
    for row in audit:
        by_source.setdefault(row["source_key"], []).append(row)
    assert by_source["51午前99"][0]["existing_question_id"] == "Q841"
    assert by_source["47午後22"][0]["existing_question_id"] == "Q1578"
    assert {row["decision"] for row in by_source["48午後89"]} == {
        "EXCLUDED_EXTRACTION_QUALITY", "EXCLUDED_DUPLICATE_INPUT_ROW"
    }
    assert by_source["48午前38"][0]["decision"] == "EXCLUDED_EXTRACTION_QUALITY"


def test_existing_nodes_reference_each_lot2_question_once_without_new_nodes():
    nodes = {row["knowledge_node_id"]: row for row in _load("knowledge_nodes.json")}
    assert len(nodes) == 1538
    for question_id, (_, _, _, _, _, node_id, _, _) in EXPECTED.items():
        assert nodes[node_id]["question_ids"].count(question_id) == 1
        assert nodes[node_id]["status"] == "confirmed_shared"


def test_lot2_does_not_change_strong_different_question_pairs():
    pairs = _load("strong_different_question_pairs.json")
    mapped = {question_id for row in pairs for question_id in row["question_ids"]}
    assert not (set(EXPECTED) & mapped)


def test_lot2_question_ids_are_contiguous_and_cross_file_ids_match():
    expected_ids = [f"Q{number}" for number in range(1, 1646)]
    for name in ("questions.json", "answers.json", "explanations.json", "question_tags.json"):
        ids = [row["id"] for row in _load(name)]
        assert ids == expected_ids
        assert len(ids) == len(set(ids)) == 1645
