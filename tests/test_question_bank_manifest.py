import copy
import json

import pytest

import question_bank
from scripts.check_question_bank_schema_manifest import check_schema_manifest


def test_runtime_declared_range_comes_from_manifest():
    result = check_schema_manifest()
    assert result["question_count"] == 1737
    assert result["first_question_number"] == 1
    assert result["last_question_number"] == 1737
    assert question_bank.QUESTION_BANK_VERSION == result["bank_version"]
    assert question_bank.EXPECTED_QUESTION_COUNT == result["question_count"]
    assert len(question_bank.EXPECTED_QUESTION_IDS) == result["question_count"]
    assert "Q1" in question_bank.EXPECTED_QUESTION_IDS
    assert "Q1737" in question_bank.EXPECTED_QUESTION_IDS


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
