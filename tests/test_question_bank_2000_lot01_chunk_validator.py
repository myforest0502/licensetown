import copy
import json
from pathlib import Path

from reports.question_bank_2000_lot01_chunk_validate import build_report


ROOT = Path(__file__).parents[1]
CHUNK = ROOT / "staging" / "question_bank_2000_lot01_chunks_v01" / "chunk_01.json"


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def test_blank_authoring_chunk_fails_closed():
    payload = read(CHUNK)
    payload["status"] = "completed_chunk"
    report = build_report(payload)
    assert report["hard_errors"]
    text = "\n".join(report["hard_errors"])
    assert "question text required" in text
    assert "single best answer required" in text
    assert "medical evidence required" in text
    assert "semantic review not accepted" in text


def test_chunk_validator_rejects_formal_qid_allocation():
    payload = read(CHUNK)
    payload["status"] = "completed_chunk"
    draft = payload["drafts"][0]
    draft["question_id"] = "Q1762"
    report = build_report(payload)
    assert any("formal Q ID allocation forbidden" in error for error in report["hard_errors"])


def test_chunk_validator_rejects_existing_demand_reuse_even_if_other_fields_change():
    payload = read(CHUNK)
    payload["status"] = "completed_chunk"
    draft = payload["drafts"][0]
    old = draft["existing_demands"][0]
    draft["proposed_task"] = old["task"]
    draft["primary_ability"] = old["primary_ability"]
    report = build_report(payload)
    assert any("candidate demand duplicates existing Node demand" in error for error in report["hard_errors"])


def test_chunk_validator_rejects_exact_duplicate_stems_inside_chunk():
    payload = read(CHUNK)
    payload["status"] = "completed_chunk"
    payload["drafts"][0]["question_text"] = "同じ問題文"
    payload["drafts"][1]["question_text"] = "同じ問題文"
    report = build_report(payload)
    assert any("exact duplicate stems inside chunk" in error for error in report["hard_errors"])
