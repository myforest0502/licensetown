import copy
import json
import re

import pytest

import question_bank
from scripts.check_question_bank_schema_manifest import check_schema_manifest


def test_runtime_declared_range_comes_from_manifest():
    result = check_schema_manifest()
    manifest = json.loads(question_bank.BANK_MANIFEST_PATH.read_text(encoding="utf-8-sig"))
    assert result["question_count"] == manifest["question_count"]
    assert result["first_question_number"] == manifest["first_question_number"]
    assert result["last_question_number"] == manifest["last_question_number"]
    assert question_bank.QUESTION_BANK_VERSION == result["bank_version"]
    assert question_bank.EXPECTED_QUESTION_COUNT == result["question_count"]
    assert len(question_bank.EXPECTED_QUESTION_IDS) == result["question_count"]
    assert "Q1" in question_bank.EXPECTED_QUESTION_IDS
    assert f"Q{result['last_question_number']}" in question_bank.EXPECTED_QUESTION_IDS
    schema_path = question_bank.BANK_MANIFEST_PATH.parent / "schema/question_bank_schema_v1.json"
    pattern = json.loads(schema_path.read_text(encoding="utf-8-sig"))["$defs"]["qid"]["pattern"]
    assert all(re.fullmatch(pattern, qid) for qid in question_bank.EXPECTED_QUESTION_IDS)
    for invalid in ("Q0", "Q01", f"Q{result['last_question_number'] + 1}", f"Q{result['last_question_number'] + 1000}"):
        assert re.fullmatch(pattern, invalid) is None


def test_manifest_range_count_contract_is_fail_closed(tmp_path):
    source = question_bank.BANK_MANIFEST_PATH
    data = json.loads(source.read_text(encoding="utf-8-sig"))
    broken = copy.deepcopy(data)
    broken["question_count"] = data["question_count"] - 1
    path = tmp_path / "bank_manifest.json"
    path.write_text(json.dumps(broken), encoding="utf-8")
    original = question_bank.BANK_MANIFEST_PATH
    try:
        question_bank.BANK_MANIFEST_PATH = path
        with pytest.raises(ValueError):
            question_bank._load_bank_manifest()
    finally:
        question_bank.BANK_MANIFEST_PATH = original
