import json
import shutil

from knowledge_node_repair_evidence import DIFFERENT_QUESTION_STRONG, classify_repair_confirmation
from reports.question_bank_2000_lot01_validate import BANK, PROTECTED, STAGING, read
from scripts.integrate_question_bank_2000_lot01 import (
    END_NODE, END_Q, QID_PATTERN, START_NODE, START_Q, TARGET_VERSION, integrate,
)


def _copy_bank(target):
    for name in PROTECTED:
        source = BANK / name
        destination = target / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)


def _index(path):
    return {row["id"]: row for row in json.loads(path.read_text(encoding="utf-8-sig"))}


def test_lot01_integrator_dry_run_is_atomic_and_idempotent(tmp_path):
    _copy_bank(tmp_path)
    canonical_before = (tmp_path / "knowledge_node_canonical_map.json").read_bytes()
    pairs_before = (tmp_path / "strong_different_question_pairs.json").read_bytes()
    integrate(tmp_path, STAGING)

    questions = _index(tmp_path / "questions.json")
    answers = _index(tmp_path / "answers.json")
    explanations = _index(tmp_path / "explanations.json")
    tags = _index(tmp_path / "question_tags.json")
    nodes = {row["knowledge_node_id"]: row for row in read(tmp_path / "knowledge_nodes.json")}
    manifest = read(tmp_path / "bank_manifest.json")
    schema = read(tmp_path / "schema/question_bank_schema_v1.json")
    drafts = read(STAGING)["drafts"]

    assert manifest == {
        "bank_version": TARGET_VERSION, "first_question_number": 1,
        "last_question_number": END_Q, "question_count": END_Q,
    }
    assert schema["$defs"]["qid"]["pattern"] == QID_PATTERN
    assert all(schema["properties"][name]["minItems"] == END_Q == schema["properties"][name]["maxItems"]
               for name in ("questions", "answers", "explanations", "question_tags"))
    expected = [f"Q{number}" for number in range(1, END_Q + 1)]
    assert all(list(store) == expected for store in (questions, answers, explanations, tags))

    new_ids = iter(f"KN{number:04d}" for number in range(START_NODE, END_NODE + 1))
    for offset, draft in enumerate(drafts):
        qid = f"Q{START_Q + offset}"
        node_id = next(new_ids) if draft["slot_type"] == "new_node" else draft["target_node_id"]
        assert questions[qid]["question_text"] == draft["question_text"]
        assert answers[qid]["answer_basis"] == "LT_original"
        assert explanations[qid]["explanation"] == draft["explanation"]
        assert tags[qid]["knowledge_node_id"] == node_id
        assert (tags[qid]["task"], tags[qid]["primary_ability"]) == (
            draft["proposed_task"], draft["primary_ability"])
        assert qid in nodes[node_id]["question_ids"]
        if draft["slot_type"] == "new_node":
            assert nodes[node_id]["status"] == "singleton_initial"
        else:
            assert nodes[node_id]["status"] == "confirmed_shared"
            for ref in draft["reference_question_ids"]:
                assert (tags[ref]["task"], tags[ref]["primary_ability"]) != (
                    tags[qid]["task"], tags[qid]["primary_ability"])

    assert (tmp_path / "knowledge_node_canonical_map.json").read_bytes() == canonical_before
    assert (tmp_path / "strong_different_question_pairs.json").read_bytes() == pairs_before
    integrate(tmp_path, STAGING)
    assert len(read(tmp_path / "questions.json")) == END_Q


def test_lot01_formal_existing_node_pairs_are_runtime_strong():
    drafts = read(STAGING)["drafts"]
    for offset, draft in enumerate(drafts):
        if draft["slot_type"] == "new_node":
            continue
        qid = f"Q{START_Q + offset}"
        for ref in draft["reference_question_ids"]:
            assert classify_repair_confirmation(ref, qid) == DIFFERENT_QUESTION_STRONG
