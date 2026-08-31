import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from adaptive_question_selector import select_node_adaptive_questions
from knowledge_node_repair_evidence import (
    DIFFERENT_QUESTION_STRONG,
    SAME_QUESTION,
    classify_repair_confirmation,
)
from knowledge_node_state_transition import derive_knowledge_node_state
from question_bank import get_answer, get_question, get_question_tag


BANK = Path(__file__).resolve().parents[1] / "data" / "question_bank"
EXPECTED_IMPORTS = {
    "Q1565": (51, "午前", 32, "5", "KN0003", "Q3"),
    "Q1566": (51, "午前", 15, "5", "KN0007", "Q7"),
    "Q1567": (49, "午前", 15, "1", "KN0067", "Q67"),
    "Q1568": (51, "午後", 42, "4", "KN0181", "Q182"),
    "Q1569": (48, "午後", 94, "4", "KN0245", "Q246"),
    "Q1570": (48, "午後", 49, "5", "KN0247", "Q248"),
    "Q1571": (50, "午前", 39, "4", "KN0273", "Q274"),
    "Q1572": (47, "午前", 28, "3", "KN0394", "Q399"),
    "Q1573": (49, "午前", 39, "5", "KN0643", "Q651"),
    "Q1574": (45, "午前", 23, "2", "KN0131", "Q131"),
}


def attempt(q_id, node, correct, confidence, at, status="answered"):
    return {
        "user_id": "test-user", "question_id": q_id,
        "knowledge_node_id": node, "is_correct": correct,
        "confidence": confidence, "answer_status": status,
        "attempted_at": at,
    }


def test_source_audited_imports_have_exact_metadata_answer_node_and_strong_pair():
    nodes = {
        item["knowledge_node_id"]: item
        for item in json.loads((BANK / "knowledge_nodes.json").read_text(encoding="utf-8-sig"))
    }
    for q_id, (exam_no, session, number, answer, node, current) in EXPECTED_IMPORTS.items():
        question = get_question(q_id)
        assert question["source"] == "P"
        assert question["exam"] == {
            "exam_no": exam_no, "session": session, "question_no": number,
        }
        assert get_answer(q_id)["display_answer"] == answer
        assert get_question_tag(q_id)["knowledge_node_id"] == node
        assert q_id in nodes[node]["question_ids"]
        assert classify_repair_confirmation(current, q_id) == DIFFERENT_QUESTION_STRONG
        assert classify_repair_confirmation(q_id, current) == DIFFERENT_QUESTION_STRONG


def test_q51_am_32_is_the_printed_peripheral_vertigo_question():
    question = get_question("Q1565")
    assert question["question_text"] == "末梢性めまいに対する理学療法で適切なのはどれか。"
    assert question["choices"]["5"] == "寝返りや振り向き動作などによる回転刺激で前庭代償を促す。"
    assert get_answer("Q1565")["display_answer"] == "5"


def test_45_am_23_resolves_to_sensitivity_node_without_changing_kn0130():
    question = get_question("Q1574")
    assert question["question_text"] == "検査の感度を示す説明で正しいのはどれか。"
    assert get_answer("Q1574")["display_answer"] == "2"
    assert get_question_tag("Q1574")["knowledge_node_id"] == "KN0131"
    nodes = {
        item["knowledge_node_id"]: item
        for item in json.loads((BANK / "knowledge_nodes.json").read_text(encoding="utf-8-sig"))
    }
    assert nodes["KN0130"]["question_ids"] == ["Q130"]
    assert nodes["KN0131"]["question_ids"] == ["Q131", "Q1574"]
    assert classify_repair_confirmation("Q131", "Q1574") == DIFFERENT_QUESTION_STRONG


def test_only_the_true_node_mismatch_and_image_dependency_are_held():
    audit = json.loads(
        (BANK / "past_exam_strong_different_q_v01_source_audit.json").read_text(encoding="utf-8-sig")
    )
    assert len(audit) == 11
    assert sum(item["import_status"].startswith("imported") for item in audit) == 10
    held = {
        item["import_status"]
        for item in audit
        if not item["import_status"].startswith("imported")
    }
    assert held == {"held_image_dependency"}


def test_same_question_does_not_become_independent_confirmation():
    assert classify_repair_confirmation("Q1565", "Q1565") == SAME_QUESTION


def test_strong_confidence_one_repairs_but_confidence_two_does_not():
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    strong = [
        attempt("Q3", "KN0003", False, 2, start),
        attempt("Q1565", "KN0003", True, 1, start + timedelta(days=1)),
    ]
    assert derive_knowledge_node_state(strong)["state"] == "repaired"
    uncertain = [
        attempt("Q7", "KN0007", False, 2, start),
        attempt("Q1566", "KN0007", True, 2, start + timedelta(days=1)),
    ]
    assert derive_knowledge_node_state(uncertain)["state"] == "repairing"


def test_same_question_success_and_unknown_remain_repairing():
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    same = [
        attempt("Q3", "KN0003", False, 2, start),
        attempt("Q3", "KN0003", True, 1, start + timedelta(days=1)),
    ]
    assert derive_knowledge_node_state(same)["state"] == "repairing"
    unknown = same + [
        attempt("Q1565", "KN0003", False, None, start + timedelta(days=2), "unknown")
    ]
    assert derive_knowledge_node_state(unknown)["state"] == "repairing"


def test_recheck_due_strong_confirmation_becomes_stable():
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    history = [
        attempt("Q3", "KN0003", False, 2, start),
        attempt("Q1565", "KN0003", True, 1, start + timedelta(days=1)),
        attempt("Q3", "KN0003", True, 1, start + timedelta(days=9)),
    ]
    assert derive_knowledge_node_state(history)["state"] == "stable"


def test_adaptive_selection_can_choose_new_strong_candidate_without_same_q_repeat():
    history = [attempt("Q3", "KN0003", False, 2, datetime(2026, 1, 1, tzinfo=timezone.utc))]
    selected = select_node_adaptive_questions(history, question_count=30)
    by_id = {item["question_id"]: item for item in selected}
    assert "Q1565" in by_id
    assert by_id["Q1565"]["strong_repair_confirmation"] is True
    assert by_id["Q1565"]["same_question_repeat"] is False
