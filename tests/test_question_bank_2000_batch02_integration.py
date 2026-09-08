import json
import shutil

from reports.question_bank_2000_batch02_validate import BANK, PROTECTED, STAGING, read
from scripts.integrate_question_bank_2000_batch02 import (
    END_Q,
    QID_PATTERN,
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


def _index(path):
    return {row["id"]: row for row in json.loads(path.read_text(encoding="utf-8-sig"))}


def test_batch02_integrator_dry_run_is_atomic_and_idempotent(tmp_path):
    _copy_bank(tmp_path)
    integrate(tmp_path, STAGING)

    manifest = read(tmp_path / "bank_manifest.json")
    schema = read(tmp_path / "schema/question_bank_schema_v1.json")
    questions = _index(tmp_path / "questions.json")
    answers = _index(tmp_path / "answers.json")
    explanations = _index(tmp_path / "explanations.json")
    tags = _index(tmp_path / "question_tags.json")
    nodes = {row["knowledge_node_id"]: row for row in read(tmp_path / "knowledge_nodes.json")}
    drafts = [row for row in read(STAGING)["drafts"] if row["status"] == "accepted"]

    assert manifest["bank_version"] == TARGET_VERSION
    assert manifest["question_count"] == manifest["last_question_number"] == END_Q
    assert schema["$defs"]["qid"]["pattern"] == QID_PATTERN
    for name in ("questions", "answers", "explanations", "question_tags"):
        assert schema["properties"][name]["minItems"] == END_Q
        assert schema["properties"][name]["maxItems"] == END_Q

    expected_ids = [f"Q{number}" for number in range(1, END_Q + 1)]
    for store in (questions, answers, explanations, tags):
        assert list(store) == expected_ids

    for offset, draft in enumerate(drafts):
        qid = f"Q{START_Q + offset}"
        ref = draft["reference_question_ids"][0]
        node = nodes[draft["target_node_id"]]
        assert node["status"] == "confirmed_shared"
        assert node["question_ids"] == [ref, qid]
        assert questions[qid]["question_text"] == draft["question_text"]
        assert tags[qid]["knowledge_node_id"] == draft["target_node_id"]
        assert (tags[qid]["task"], tags[qid]["primary_ability"]) == (
            draft["proposed_task"], draft["primary_ability"]
        )
        assert (tags[ref]["task"], tags[ref]["primary_ability"]) != (
            tags[qid]["task"], tags[qid]["primary_ability"]
        )
        assert answers[qid]["answer_basis"] == "LT_original"
        assert explanations[qid]["explanation"] == draft["explanation"]

    # A second execution must not duplicate records or mutate the contract again.
    integrate(tmp_path, STAGING)
    assert len(read(tmp_path / "questions.json")) == END_Q
    assert read(tmp_path / "bank_manifest.json")["question_count"] == END_Q
