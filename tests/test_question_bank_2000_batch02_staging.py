import copy
import json
import shutil

import pytest

from reports.question_bank_2000_batch02_validate import (
    BANK,
    PROTECTED,
    STAGING,
    build_report,
    draft_fingerprint,
    file_fingerprint,
    normalize,
    read,
)


@pytest.fixture
def payload():
    return read(STAGING)


def test_accepted_set_and_current_formal_contract(payload):
    report = build_report(payload)
    assert report["hard_errors"] == []
    assert report["accepted_count"] == report["unique_targets"] == 12
    if report["lifecycle"] == "staging":
        assert report["formal_count"] == 1749
        assert report["integrated_count"] == 0
    else:
        assert report["lifecycle"] == "integrated"
        assert report["formal_count"] == 1761
        assert report["integrated_count"] == 12
    assert report["exact_formal_duplicates"] == report["exact_candidate_duplicates"] == []
    assert report["category_counts"] == {9: 4, 18: 3, 17: 3, 16: 2}
    assert report["safety_counts"] == {"none": 4, "moderate": 5, "critical": 3}
    assert {d["draft_id"] for d in payload["drafts"]} == {f"B02-{n:02}" for n in range(1, 13)}
    assert "KN0779" not in {d["target_node_id"] for d in payload["drafts"]}


@pytest.mark.parametrize("key,value,message", [
    ("target_node_id", "KN9999", "target Node missing"),
    ("target_node_id", "KN0779", "excluded Node"),
    ("target_node_id", "KN0007", "excluded Node"),
    ("reference_question_ids", ["Q99999"], "reference absent"),
    ("reference_question_ids", ["Q583"], "Node/reference registry mismatch"),
    ("proposed_category_small", 18, "category mismatch"),
    ("proposed_category_large", "C", "category mismatch"),
    ("expected_target_state", "multi", "target staging state contract changed"),
    ("primary_ability", "DECIDE", "task/ability mismatch"),
    ("correct_choices", ["1", "2"], "single best answer"),
    ("correct_choices", ["6"], "single best answer"),
    ("choices", {"1": "一択"}, "five choices"),
    ("choice_explanations", {}, "five choices"),
    ("question_id", "Q99999", "Q ID allocation forbidden"),
    ("source", "past_exam", "source must be original"),
    ("evidence", [], "medical sources missing"),
    ("semantic_review", {}, "semantic decision missing"),
    ("question_text", "編集された問題文。", "content changed after semantic review"),
])
def test_validator_rejects_invalid_draft(payload, key, value, message):
    payload["drafts"][0][key] = value
    assert any(message in error for error in build_report(payload)["hard_errors"])


def test_count_and_duplicate_ids_targets_fail_closed(payload):
    payload["drafts"].append(copy.deepcopy(payload["drafts"][0]))
    errors = build_report(payload)["hard_errors"]
    for message in ("accepted count", "duplicate draft ID", "duplicate accepted canonical target", "exact candidate duplicate"):
        assert any(message in error for error in errors)


def test_changed_label_cannot_accept_a_copied_reference(payload):
    draft = payload["drafts"][0]
    draft["question_text"] = draft["reference_snapshot"]["question_text"]
    draft["reviewed_sha256"] = draft_fingerprint(draft)
    assert any("exact formal duplicate" in e for e in build_report(payload)["hard_errors"])


def test_near_rewrite_is_not_accepted_by_new_metadata(payload):
    draft = payload["drafts"][0]
    draft["question_text"] = draft["reference_snapshot"]["question_text"].replace("79歳", "80歳")
    draft["reviewed_sha256"] = draft_fingerprint(draft)
    errors = build_report(payload)["hard_errors"]
    assert any("near formal stem" in e for e in errors)


def test_same_demand_cannot_be_accepted_by_renewing_seal(payload):
    draft = payload["drafts"][0]
    draft["proposed_task"] = draft["reference_snapshot"]["task"]
    draft["primary_ability"] = draft["reference_snapshot"]["primary_ability"]
    draft["semantic_review"]["candidate_demand"] = draft["semantic_review"]["reference_demand"]
    draft["reviewed_sha256"] = draft_fingerprint(draft)
    errors = build_report(payload)["hard_errors"]
    assert any("same metadata demand" in e for e in errors)
    assert any("same semantic demand" in e for e in errors)


@pytest.mark.parametrize("mutation", [
    "missing_answer",
    "registry_state",
    "second_canonical_question",
])
def test_changed_formal_state_invalidates_review(payload, tmp_path, mutation):
    current = build_report(payload)
    for name in PROTECTED:
        target = tmp_path / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(BANK / name, target)
    if mutation == "missing_answer":
        path = tmp_path / "answers.json"
        data = [r for r in read(path) if r["id"] != "Q117"]
    elif mutation == "registry_state":
        path = tmp_path / "knowledge_nodes.json"
        data = read(path)
        node = next(r for r in data if r["knowledge_node_id"] == "KN0117")
        node["status"] = "singleton_initial" if current["lifecycle"] == "integrated" else "confirmed_shared"
    else:
        path = tmp_path / "question_tags.json"
        data = read(path)
        next(r for r in data if r["id"] == "Q583")["knowledge_node_id"] = "KN0117"
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    errors = build_report(payload, tmp_path)["hard_errors"]
    assert errors
    if mutation == "missing_answer":
        assert any("four-store ID order/count mismatch" in e or "reference absent" in e for e in errors)
    elif mutation == "registry_state":
        assert any("registry state" in e for e in errors)
    else:
        assert any("target not canonical" in e or "Node/reference registry mismatch" in e for e in errors)


def test_normalization_ignores_spacing_punctuation_and_width():
    assert normalize("ＡＢＣ　１２？\n") == normalize("abc12")


def test_formal_hash_is_portable_but_detects_content_changes(tmp_path):
    path = tmp_path / "sample.json"
    path.write_bytes(b'{\n  "value": 1\n}\n')
    original = file_fingerprint(path)
    path.write_bytes(b'{\r\n  "value": 1\r\n}\r\n')
    assert file_fingerprint(path) == original
    path.write_bytes(b'{\r\n  "value": 2\r\n}\r\n')
    assert file_fingerprint(path) != original


def test_answer_and_review_edits_invalidate_content_seal(payload):
    draft = payload["drafts"][0]
    for field in ("choices", "choice_explanations", "semantic_review"):
        changed = copy.deepcopy(draft)
        changed[field][next(iter(changed[field]))] = "変更"
        assert draft_fingerprint(changed) != draft["reviewed_sha256"]
