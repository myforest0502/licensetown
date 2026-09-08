"""Merge six completed Lot03 8-draft authoring chunks into one staging lot."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHUNK_DIR = ROOT / "staging" / "question_bank_2000_lot03_chunks_v01"
FINAL = ROOT / "staging" / "question_bank_2000_lot03_v01.json"
CHUNK_SIZE = 8
CHUNK_COUNT = 6
FORMAL_BASELINE = "Q1-Q1857"


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def merge() -> None:
    completed = []
    for index in range(1, CHUNK_COUNT + 1):
        path = CHUNK_DIR / f"chunk_{index:02d}.json"
        payload = read(path)
        if payload.get("formal_baseline") != FORMAL_BASELINE:
            raise ValueError(f"chunk {index:02d} baseline mismatch")
        if payload.get("status") != "completed_chunk":
            raise ValueError(f"chunk {index:02d} is not completed_chunk")
        if len(payload.get("drafts", [])) != CHUNK_SIZE:
            raise ValueError(f"chunk {index:02d} does not contain eight drafts")
        completed.extend(payload["drafts"])

    ids = [d.get("draft_id") for d in completed]
    if len(ids) != 48 or len(set(ids)) != 48 or any(not value for value in ids):
        raise ValueError("completed chunk draft IDs must be 48 unique nonblank values")

    final = {
        "batch": "question_bank_2000_production_lot03_v01",
        "formal_baseline": FORMAL_BASELINE,
        "q_ids_reserved": False,
        "production_write": False,
        "db_write": False,
        "accepted_target_count": 48,
        "status": "staging_only",
        "drafts": completed,
        "chunk_merge_provenance": {
            "scheme": "6x8-authoring-only-v1",
            "chunks": [f"question_bank_2000_lot03_chunks_v01/chunk_{i:02d}.json" for i in range(1, 7)],
        },
    }
    for draft in final["drafts"]:
        draft["status"] = "accepted"
        draft["reviewed_sha256"] = ""
    FINAL.write_text(json.dumps(final, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"merged": 48, "output": str(FINAL.relative_to(ROOT)), "sealed": False}, ensure_ascii=False))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("merge",))
    parser.parse_args()
    merge()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
