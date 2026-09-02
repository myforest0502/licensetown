import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from adaptive_question_selector import select_node_adaptive_questions
from knowledge_node_repair_evidence import DIFFERENT_QUESTION_STRONG, classify_repair_confirmation
from knowledge_node_repairability import STRONG_ALT, build_repairability_audit
from knowledge_node_state_transition import derive_knowledge_node_state
from question_bank import get_answer, get_explanation, get_question, get_question_tag, question_count


BANK = Path(__file__).resolve().parents[1] / "data" / "question_bank"
PAIRS = {
    "Q1595": ("Q8", "KN0008", "safety_priority", "DECIDE"),
    "Q1596": ("Q25", "KN0025", "finding_interpretation", "INTERPRET"),
    "Q1597": ("Q36", "KN0036", "finding_interpretation", "INTERPRET"),
    "Q1598": ("Q109", "KN0109", "assessment_selection", "MEASURE"),
    "Q1599": ("Q195", "KN0194", "finding_interpretation", "INTERPRET"),
    "Q1600": ("Q331", "KN0329", "finding_interpretation", "INTERPRET"),
    "Q1601": ("Q379", "KN0374", "safety_priority", "DECIDE"),
    "Q1602": ("Q684", "KN0676", "safety_priority", "DECIDE"),
    "Q1603": ("Q705", "KN0697", "assessment_selection", "MEASURE"),
    "Q1604": ("Q1305", "KN1288", "finding_interpretation", "INTERPRET"),
    "Q1605": ("Q1504", "KN1479", "intervention_selection", "PRESCRIBE"),
}


def attempt(q_id, node_id, correct, confidence, at, status="answered"):
    return {
        "user_id": "pilot-test",
        "question_id": q_id,
        "knowledge_node_id": node_id,
        "is_correct": correct,
        "confidence": confidence,
        "answer_status": status,
        "attempted_at": at,
        "answered_at": at,
    }


def test_all_eleven_original_questions_have_complete_records_and_formal_strong_pairs():
    assert question_count() == 1640
    for new_q, (source_q, node_id, task, ability) in PAIRS.items():
        question = get_question(new_q)
        answer = get_answer(new_q)
        explanation = get_explanation(new_q)
        tag = get_question_tag(new_q)
        assert question["source"] == "O" and question["exam"] is None
        assert question["management_code"].endswith("-O")
        assert len(question["choices"]) == 5
        assert answer["answer_basis"] == "LT_original"
        assert answer["accepted_answer_sets"]
        assert set(explanation["choice_explanations"]) == set(question["choices"])
        assert tag["knowledge_node_id"] == node_id
        assert tag["task"] == task and tag["primary_ability"] == ability
        assert tag["safety"] == "moderate"
        assert tag["source"] == "original"
        assert classify_repair_confirmation(source_q, new_q) == DIFFERENT_QUESTION_STRONG
        assert classify_repair_confirmation(new_q, source_q) == DIFFERENT_QUESTION_STRONG


def test_new_ids_are_contiguous_and_nodes_are_confirmed_shared():
    files = ("questions.json", "answers.json", "explanations.json", "question_tags.json")
    expected = {f"Q{number}" for number in range(1595, 1606)}
    for filename in files:
        records = json.loads((BANK / filename).read_text(encoding="utf-8-sig"))
        ids = [item["id"] for item in records]
        assert len(ids) == len(set(ids)) == 1640
        assert expected.issubset(ids)
    nodes = {
        item["knowledge_node_id"]: item
        for item in json.loads((BANK / "knowledge_nodes.json").read_text(encoding="utf-8-sig"))
    }
    for new_q, (source_q, node_id, _task, _ability) in PAIRS.items():
        assert nodes[node_id]["status"] == "confirmed_shared"
        assert source_q in nodes[node_id]["question_ids"]
        assert new_q in nodes[node_id]["question_ids"]


def test_static_repairability_reports_all_eleven_as_strong_available():
    by_node = {item["canonical_node_id"]: item for item in build_repairability_audit()}
    for new_q, (source_q, node_id, _task, _ability) in PAIRS.items():
        item = by_node[node_id]
        assert item["classification"] == STRONG_ALT
        assert item["repairable"] is True
        assert [source_q, new_q] in item["strong_alt_pairs"]


def test_formal_transition_repairs_only_with_strong_different_q_confidence_one():
    start = datetime(2026, 9, 1, tzinfo=timezone.utc)
    wrong = attempt("Q379", "KN0374", False, 1, start)
    strong = attempt("Q1601", "KN0374", True, 1, start + timedelta(hours=1))
    assert derive_knowledge_node_state([wrong, strong])["state"] == "repaired"
    uncertain = {**strong, "confidence": 2}
    assert derive_knowledge_node_state([wrong, uncertain])["state"] == "repairing"
    same_q = {**strong, "question_id": "Q379"}
    assert derive_knowledge_node_state([wrong, same_q])["state"] == "repairing"
    unknown = {**strong, "is_correct": False, "confidence": None, "answer_status": "unknown"}
    assert derive_knowledge_node_state([wrong, unknown])["state"] == "repairing"


def test_recent_safety_source_prefers_non_recent_strong_alternate_without_bypass():
    now = datetime(2026, 9, 1, tzinfo=timezone.utc)
    selected = select_node_adaptive_questions(
        [attempt("Q379", "KN0374", False, 1, now)],
        question_count=30,
    )
    by_id = {item["question_id"]: item for item in selected}
    assert "Q1601" in by_id
    assert "Q379" not in by_id
    assert by_id["Q1601"]["repair_evidence_quality"] == DIFFERENT_QUESTION_STRONG
    assert by_id["Q1601"]["recent_question_repeat"] is False
    assert by_id["Q1601"]["recent_cooldown_bypassed"] is False
