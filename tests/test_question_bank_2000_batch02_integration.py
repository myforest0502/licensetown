import json
import shutil

from knowledge_node_repair_evidence import (
    DIFFERENT_QUESTION_STRONG,
    classify_repair_confirmation,
)
from reports.question_bank_2000_batch02_validate import (
    BANK,
    PROTECTED,
    STAGING,
    build_report,
    read,
)
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


def test_batch02_remains_a_formal_milestone_after_later_lots():
    manifest = read(BANK / "bank_manifest.json")
    schema = read(BANK / "schema/question_bank_schema_v1.json")
    questions = _index(BANK / "questions.json")
    answers = _index(BANK / "answers.json")
    explanations = _index(BANK / "explanations.json")
    tags = _index(BANK / "question_tags.json")
    nodes = {row["knowledge_node_id"]: row for row in read(BANK / "knowledge_nodes.json")}
    payload = read(STAGING)
    drafts = [row for row in payload["drafts"] if row["status"] == "accepted"]

    assert manifest["question_count"] == manifest["last_question_number"] >= END_Q
    for name in ("questions", "answers", "explanations", "question_tags"):
        assert schema["properties"][name]["minItems"] == manifest["question_count"]
        assert schema["properties"][name]["maxItems"] == manifest["question_count"]

    expected_ids = [f"Q{number}" for number in range(1, manifest["question_count"] + 1)]
    for store in (questions, answers, explanations, tags):
        assert list(store) == expected_ids

    for offset, draft in enumerate(drafts):
        qid = f"Q{START_Q + offset}"
        ref = draft["reference_question_ids"][0]
        node = nodes[draft["target_node_id"]]
        assert node["status"] == "confirmed_shared"
        assert node["question_ids"][:2] == [ref, qid]
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

    report = build_report(payload, BANK)
    assert report["hard_errors"] == []
    assert report["lifecycle"] == "integrated"
    assert report["integrated_count"] == 12
    assert report["formal_count"] == manifest["question_count"]


def test_batch02_formal_pairs_are_runtime_strong_repair_evidence():
    payload = read(STAGING)
    drafts = [row for row in payload["drafts"] if row["status"] == "accepted"]
    assert len(drafts) == 12

    for offset, draft in enumerate(drafts):
        ref = draft["reference_question_ids"][0]
        qid = f"Q{START_Q + offset}"
        assert classify_repair_confirmation(ref, qid) == DIFFERENT_QUESTION_STRONG
