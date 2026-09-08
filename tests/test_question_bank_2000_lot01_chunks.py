import copy
import json
from pathlib import Path

import pytest

from reports import question_bank_2000_lot01_chunks as chunks


ROOT = Path(__file__).parents[1]
SEED = ROOT / "staging" / "question_bank_2000_lot01_authoring_seed_v01.json"
CHUNK_DIR = ROOT / "staging" / "question_bank_2000_lot01_chunks_v01"


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def test_committed_chunk_set_is_exactly_six_by_eight_and_matches_seed_order():
    seed = read(SEED)
    expected_ids = [d["draft_id"] for d in seed["drafts"]]
    actual_ids = []
    assert len(expected_ids) == 48
    for index in range(1, 7):
        payload = read(CHUNK_DIR / f"chunk_{index:02d}.json")
        assert payload["lot"] == "question_bank_2000_production_lot01_v01"
        assert payload["chunk"] == index
        assert payload["chunk_count"] == 6
        assert payload["status"] == "authoring_chunk"
        assert payload["q_ids_reserved"] is False
        assert payload["production_write"] is False
        assert payload["db_write"] is False
        assert len(payload["drafts"]) == 8
        actual_ids.extend(d["draft_id"] for d in payload["drafts"])
    assert actual_ids == expected_ids
    assert len(set(actual_ids)) == 48


def test_merge_rejects_any_incomplete_chunk(tmp_path, monkeypatch):
    seed = read(SEED)
    chunk_dir = tmp_path / "chunks"
    chunk_dir.mkdir()
    for index in range(1, 7):
        subset = seed["drafts"][(index - 1) * 8:index * 8]
        payload = {
            "lot": "question_bank_2000_production_lot01_v01",
            "chunk": index,
            "chunk_count": 6,
            "status": "completed_chunk" if index != 4 else "authoring_chunk",
            "drafts": copy.deepcopy(subset),
        }
        (chunk_dir / f"chunk_{index:02d}.json").write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    monkeypatch.setattr(chunks, "CHUNK_DIR", chunk_dir)
    monkeypatch.setattr(chunks, "FINAL", tmp_path / "final.json")
    with pytest.raises(ValueError, match="chunk 04 is not completed_chunk"):
        chunks.merge()


def test_merge_rejects_reordered_or_duplicate_draft_ids(tmp_path, monkeypatch):
    seed = read(SEED)
    chunk_dir = tmp_path / "chunks"
    chunk_dir.mkdir()
    for index in range(1, 7):
        subset = copy.deepcopy(seed["drafts"][(index - 1) * 8:index * 8])
        if index == 2:
            subset[0]["draft_id"] = subset[1]["draft_id"]
        payload = {
            "lot": "question_bank_2000_production_lot01_v01",
            "chunk": index,
            "chunk_count": 6,
            "status": "completed_chunk",
            "drafts": subset,
        }
        (chunk_dir / f"chunk_{index:02d}.json").write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    monkeypatch.setattr(chunks, "CHUNK_DIR", chunk_dir)
    monkeypatch.setattr(chunks, "FINAL", tmp_path / "final.json")
    with pytest.raises(ValueError, match="draft IDs/order"):
        chunks.merge()
