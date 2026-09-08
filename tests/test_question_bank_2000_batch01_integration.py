import json
from pathlib import Path

from reports.question_bank_2000_batch01_validate import (
    END_Q,
    START_Q,
    _accepted_drafts,
    _choice_map,
    _correct_letters,
    build_report,
)

ROOT = Path(__file__).resolve().parents[1]
BANK = ROOT / "data" / "question_bank"


def _read(name):
    return json.loads((BANK / name).read_text(encoding="utf-8-sig"))


def test_batch01_is_fully_integrated_and_manifest_advanced():
    report = build_report()
    assert report["accepted_count"] == 12
    assert report["integrated_count"] == 12
    assert report["hard_errors"] == [], "\n" + "\n".join(report["hard_errors"])

    manifest = _read("bank_manifest.json")
    assert manifest["bank_version"] == "2026-09-b13"
    assert manifest["last_question_number"] == END_Q
    assert manifest["question_count"] == END_Q


def test_batch01_four_formal_stores_are_contiguous_and_aligned():
    stores = [_read(name) for name in (
        "questions.json",
        "answers.json",
        "explanations.json",
        "question_tags.json",
    )]
    expected_ids = [f"Q{number}" for number in range(1, END_Q + 1)]
    for store in stores:
        assert [row["id"] for row in store] == expected_ids


def test_batch01_formal_records_match_accepted_drafts_and_nodes():
    questions = {row["id"]: row for row in _read("questions.json")}
    answers = {row["id"]: row for row in _read("answers.json")}
    explanations = {row["id"]: row for row in _read("explanations.json")}
    tags = {row["id"]: row for row in _read("question_tags.json")}
    nodes = {row["knowledge_node_id"]: row for row in _read("knowledge_nodes.json")}

    drafts = _accepted_drafts()
    assert len(drafts) == END_Q - START_Q + 1 == 12
    assert "KN0779" not in {draft["target_node_id"] for draft in drafts}

    for offset, draft in enumerate(drafts):
        qid = f"Q{START_Q + offset}"
        ref_qid = str(draft["reference_question_ids"][0])
        node_id = str(draft["target_node_id"])
        question = questions[qid]
        answer = answers[qid]
        explanation = explanations[qid]
        tag = tags[qid]
        node = nodes[node_id]

        assert question["category_large"] == draft["proposed_category_large"]
        assert question["category_small"] == int(draft["proposed_category_small"])
        assert question["source"] == "O"
        assert question["title"] == draft.get("title")
        assert question["question_text"] == draft["question_text"]
        assert question["choices"] == _choice_map(draft["choices"])
        assert question["exam"] is None

        correct = _correct_letters(draft["correct_choices"])
        assert answer["display_answer"] == correct[0]
        assert answer["accepted_answer_sets"] == [correct]
        assert answer["answer_basis"] == "LT_original"

        assert explanation["explanation"] == draft["explanation"]
        assert explanation["choice_explanations"] == _choice_map(draft["choice_explanations"])

        assert tag["knowledge_node_id"] == node_id
        assert tag["task"] == draft["proposed_task"]
        assert tag["primary_ability"] == draft["primary_ability"]
        assert tag["secondary_ability"] == draft.get("secondary_ability")
        assert tag["level"] == int(draft["level"])
        assert tag["safety"] == draft["safety"]
        assert tag["tag_version"] == "1.0"
        assert tag["tag_status"] == "reviewed"
        assert tag["source"] == "original"

        assert node["status"] == "confirmed_shared"
        assert node["question_ids"] == [ref_qid, qid]
