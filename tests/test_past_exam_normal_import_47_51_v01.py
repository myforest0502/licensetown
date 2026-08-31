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
    "Q1575": (50, "午後", 90, "3", "KN0686", "Q694", 16),
    "Q1576": (50, "午前", 52, "1", "KN0726", "Q734", 1),
    "Q1577": (49, "午後", 37, "5", "KN0645", "Q653", 18),
    "Q1578": (47, "午後", 22, "2", "KN0547", "Q555", 5),
    "Q1579": (47, "午前", 86, "3", "KN0779", "Q787", 17),
    "Q1580": (47, "午後", 47, "4", "KN0412", "Q419", 18),
    "Q1581": (49, "午後", 89, "3", "KN0513", "Q521", 9),
    "Q1582": (49, "午前", 32, "3", "KN0373", "Q378", 11),
    "Q1583": (51, "午前", 96, "1", "KN0713", "Q721", 18),
    "Q1584": (49, "午後", 34, "3", "KN0323", "Q325", 17),
    "Q1585": (49, "午前", 68, "3・4", "KN0659", "Q667", 2),
    "Q1586": (50, "午前", 38, "2", "KN0717", "Q725", 18),
    "Q1587": (49, "午後", 85, "4", "KN0598", "Q606", 8),
    "Q1588": (51, "午後", 38, "1", "KN0576", "Q584", 18),
    "Q1589": (49, "午後", 61, "1／4／5（いずれも正答扱い）", "KN0731", "Q739", 2),
    "Q1590": (50, "午後", 39, "1", "KN0305", "Q307", 18),
    "Q1591": (47, "午後", 59, "1", "KN0534", "Q542", 1),
}


def _load(name):
    return json.loads((DATA / name).read_text(encoding="utf-8-sig"))


def test_imported_questions_keep_official_exam_answer_and_reviewed_node():
    assert question_count() == 1591
    for question_id, (exam_no, session, question_no, answer, node_id, _, category) in EXPECTED.items():
        question = get_question(question_id)
        assert question["source"] == "P"
        assert question["exam"] == {
            "exam_no": exam_no,
            "session": session,
            "question_no": question_no,
        }
        assert question["category_small"] == category
        assert get_answer(question_id)["display_answer"] == answer
        assert len(get_explanation(question_id)["choice_explanations"]) == 5
        tag = get_question_tag(question_id)
        assert tag["knowledge_node_id"] == node_id
        assert tag["tag_version"] == "1.0"
        assert tag["tag_status"] == "reviewed"
        assert tag["source"] == "past_exam"


def test_multiple_official_answers_are_not_flattened():
    assert get_answer("Q1585")["accepted_answer_sets"] == [["3", "4"]]
    assert get_answer("Q1589")["accepted_answer_sets"] == [["1"], ["4"], ["5"]]


def test_existing_nodes_reference_each_new_question_once():
    nodes = {row["knowledge_node_id"]: row for row in _load("knowledge_nodes.json")}
    for question_id, (_, _, _, _, node_id, paired_question_id, _) in EXPECTED.items():
        question_ids = nodes[node_id]["question_ids"]
        assert question_ids.count(question_id) == 1
        assert paired_question_id in question_ids


def test_source_audit_covers_all_21_candidates_and_documents_holds():
    audit = _load("past_exam_normal_import_47_51_v01_source_audit.json")
    assert len(audit) == 21
    decisions = {row["source_key"]: row["decision"] for row in audit}
    assert list(decisions.values()).count("IMPORTED") == 17
    assert decisions["50午後65"] == "HOLD"
    assert decisions["51午後99"] == "HOLD"
    assert decisions["48午前80"] == "EXCLUDED_DUPLICATE"
    assert decisions["51午後92"] == "EXCLUDED_DUPLICATE"


def test_no_strong_relation_was_added_by_normal_import():
    pairs = _load("strong_different_question_pairs.json")
    mapped = {question_id for row in pairs for question_id in row["question_ids"]}
    assert not (set(EXPECTED) & mapped)


def test_question_ids_are_contiguous_and_cross_file_ids_match():
    collections = [_load(name) for name in (
        "questions.json",
        "answers.json",
        "explanations.json",
        "question_tags.json",
    )]
    expected_ids = [f"Q{number}" for number in range(1, 1592)]
    for rows in collections:
        ids = [row["id"] for row in rows]
        assert ids == expected_ids
        assert len(ids) == len(set(ids)) == 1591
