import json
import shutil

from reports.question_bank_2000_lot02_validate import BANK, PROTECTED, STAGING, read
from scripts.integrate_question_bank_2000_lot02 import (
    END_NODE,
    END_Q,
    QID_PATTERN,
    START_NODE,
    START_Q,
    TARGET_VERSION,
    integrate,
)


def _copy_bank(tmp_path):
    for name in PROTECTED:
        source = BANK / name
        target = tmp_path / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)


def _read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _index(path):
    return {row["id"]: row for row in _read(path)}


def test_lot02_integrator_is_atomic_idempotent_and_allocates_q1810_q1857(tmp_path):
    live_manifest = read(BANK / "bank_manifest.json")
    if live_manifest["last_question_number"] > END_Q:
        return
    _copy_bank(tmp_path)
    canonical_before = (tmp_path / "knowledge_node_canonical_map.json").read_bytes()
    strong_before = (tmp_path / "strong_different_question_pairs.json").read_bytes()

    integrate(tmp_path, STAGING)
    # A completed integration must be safe to run again without duplicating rows.
    integrate(tmp_path, STAGING)

    manifest = read(tmp_path / "bank_manifest.json")
    schema = read(tmp_path / "schema/question_bank_schema_v1.json")
    questions = _index(tmp_path / "questions.json")
    answers = _index(tmp_path / "answers.json")
    explanations = _index(tmp_path / "explanations.json")
    tags = _index(tmp_path / "question_tags.json")
    nodes = {row["knowledge_node_id"]: row for row in read(tmp_path / "knowledge_nodes.json")}
    payload = read(STAGING)
    drafts = payload["drafts"]

    assert manifest == {
        "bank_version": TARGET_VERSION,
        "first_question_number": 1,
        "last_question_number": END_Q,
        "question_count": END_Q,
    }
    assert schema["$defs"]["qid"]["pattern"] == QID_PATTERN
    for name in ("questions", "answers", "explanations", "question_tags"):
        assert schema["properties"][name]["minItems"] == END_Q
        assert schema["properties"][name]["maxItems"] == END_Q

    expected_ids = [f"Q{number}" for number in range(1, END_Q + 1)]
    for store in (questions, answers, explanations, tags):
        assert list(store) == expected_ids

    new_node_ids = [f"KN{number:04d}" for number in range(START_NODE, END_NODE + 1)]
    new_cursor = 0
    for offset, draft in enumerate(drafts):
        qid = f"Q{START_Q + offset}"
        assert questions[qid]["question_text"] == draft["question_text"]
        assert answers[qid]["answer_basis"] == "LT_original"
        assert explanations[qid]["explanation"] == draft["explanation"]
        assert (tags[qid]["task"], tags[qid]["primary_ability"]) == (
            draft["proposed_task"], draft["primary_ability"]
        )

        if draft["slot_type"] == "new_node":
            node_id = new_node_ids[new_cursor]
            new_cursor += 1
            assert tags[qid]["knowledge_node_id"] == node_id
            assert nodes[node_id]["label"] == draft["target_node_label"]
            assert nodes[node_id]["status"] == "singleton_initial"
            assert nodes[node_id]["question_ids"] == [qid]
        else:
            node_id = draft["target_node_id"]
            assert tags[qid]["knowledge_node_id"] == node_id
            assert nodes[node_id]["status"] == "confirmed_shared"
            assert nodes[node_id]["question_ids"][-1] == qid
            reference_tags = [tags[ref] for ref in draft["reference_question_ids"]]
            reference_demands = {
                (row["task"], row["primary_ability"]) for row in reference_tags
            }
            assert (tags[qid]["task"], tags[qid]["primary_ability"]) not in reference_demands

    assert new_cursor == 4
    assert (tmp_path / "knowledge_node_canonical_map.json").read_bytes() == canonical_before
    assert (tmp_path / "strong_different_question_pairs.json").read_bytes() == strong_before
