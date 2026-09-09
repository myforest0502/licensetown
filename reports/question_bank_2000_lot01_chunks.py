"""Split Lot01 authoring seed into six 8-draft work chunks and merge completed chunks.

Chunking is an authoring-efficiency mechanism only. Lot01 remains one 48-question
staging/formal lot; no chunk can be sealed, allocated Q IDs, or integrated alone.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEED = ROOT / "staging" / "question_bank_2000_lot01_authoring_seed_v01.json"
CHUNK_DIR = ROOT / "staging" / "question_bank_2000_lot01_chunks_v01"
FINAL = ROOT / "staging" / "question_bank_2000_lot01_v01.json"
CHUNK_SIZE = 8
CHUNK_COUNT = 6


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def split() -> None:
    seed = read(SEED)
    drafts = seed["drafts"]
    if len(drafts) != CHUNK_SIZE * CHUNK_COUNT:
        raise ValueError(f"expected 48 seed drafts, got {len(drafts)}")
    CHUNK_DIR.mkdir(parents=True, exist_ok=True)
    for index in range(CHUNK_COUNT):
        subset = drafts[index * CHUNK_SIZE:(index + 1) * CHUNK_SIZE]
        payload = {
            "lot":"question_bank_2000_production_lot01_v01",
            "chunk":index + 1,
            "chunk_count":CHUNK_COUNT,
            "status":"authoring_chunk",
            "formal_baseline":"Q1-Q1761",
            "q_ids_reserved":False,
            "production_write":False,
            "db_write":False,
            "drafts":subset,
            "rules":[
                "This is one authoring chunk of Lot01, not an independently integrable batch.",
                "Do not allocate Q IDs or Knowledge Node IDs.",
                "Fill only these eight drafts and preserve draft_id/slot/target/reference fields.",
                "Suggested task/level/Safety may change only for medical quality; final 48-lot quotas are reconciled after all chunks.",
                "Every completed draft needs evidence and honest semantic review.",
            ],
        }
        path = CHUNK_DIR / f"chunk_{index + 1:02d}.json"
        path.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"chunks":CHUNK_COUNT,"drafts_per_chunk":CHUNK_SIZE,"total":len(drafts)},ensure_ascii=False))


def merge() -> None:
    seed = read(SEED)
    expected_ids = [d["draft_id"] for d in seed["drafts"]]
    completed = []
    for index in range(1, CHUNK_COUNT + 1):
        path = CHUNK_DIR / f"chunk_{index:02d}.json"
        payload = read(path)
        if payload.get("status") != "completed_chunk":
            raise ValueError(f"chunk {index:02d} is not completed_chunk")
        if len(payload.get("drafts", [])) != CHUNK_SIZE:
            raise ValueError(f"chunk {index:02d} does not contain eight drafts")
        completed.extend(payload["drafts"])
    ids = [d.get("draft_id") for d in completed]
    if ids != expected_ids or len(set(ids)) != 48:
        raise ValueError("completed chunk draft IDs/order do not exactly match the authoring seed")
    final = {
        **{k:v for k,v in seed.items() if k not in {"drafts","seed_warning"}},
        "status":"staging_only",
        "drafts":completed,
        "chunk_merge_provenance":{
            "scheme":"6x8-authoring-only-v1",
            "chunks":[f"question_bank_2000_lot01_chunks_v01/chunk_{i:02d}.json" for i in range(1,7)],
        },
    }
    # Seals are deliberately absent here. The Lot01 seal tool performs the full
    # 48-question validator and only then writes formal/draft hashes.
    final.pop("formal_input_sha256", None)
    final.pop("formal_hash_format", None)
    for draft in final["drafts"]:
        draft["status"] = "accepted"
        draft["reviewed_sha256"] = ""
    FINAL.write_text(json.dumps(final,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"merged":48,"output":str(FINAL.relative_to(ROOT)),"sealed":False},ensure_ascii=False))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("split","merge"))
    args = parser.parse_args()
    split() if args.mode == "split" else merge()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
