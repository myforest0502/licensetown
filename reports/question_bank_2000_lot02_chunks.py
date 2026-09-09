"""Split Lot02 authoring seed into six 8-draft chunks and merge completed chunks.

Chunking is authoring-only. Lot02 remains one 48-question staging/formal lot; no
individual chunk may be sealed, allocated Q IDs, or integrated by itself.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEED = ROOT / "staging" / "question_bank_2000_lot02_authoring_seed_v01.json"
CHUNK_DIR = ROOT / "staging" / "question_bank_2000_lot02_chunks_v01"
FINAL = ROOT / "staging" / "question_bank_2000_lot02_v01.json"
CHUNK_SIZE = 8
CHUNK_COUNT = 6
FORMAL_BASELINE = "Q1-Q1809"


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def split() -> None:
    seed = read(SEED)
    if seed.get("formal_baseline") != FORMAL_BASELINE:
        raise ValueError(f"unexpected Lot02 seed baseline: {seed.get('formal_baseline')}")
    drafts = seed["drafts"]
    if len(drafts) != CHUNK_SIZE * CHUNK_COUNT:
        raise ValueError(f"expected 48 seed drafts, got {len(drafts)}")
    if len({d.get("draft_id") for d in drafts}) != 48:
        raise ValueError("Lot02 seed draft IDs are not unique")

    CHUNK_DIR.mkdir(parents=True, exist_ok=True)
    for index in range(CHUNK_COUNT):
        subset = drafts[index * CHUNK_SIZE : (index + 1) * CHUNK_SIZE]
        payload = {
            "lot": "question_bank_2000_production_lot02_v01",
            "chunk": index + 1,
            "chunk_count": CHUNK_COUNT,
            "status": "authoring_chunk",
            "formal_baseline": FORMAL_BASELINE,
            "q_ids_reserved": False,
            "production_write": False,
            "db_write": False,
            "drafts": subset,
            "rules": [
                "This is one authoring chunk of Lot02, not an independently integrable batch.",
                "Do not allocate Q IDs or Knowledge Node IDs.",
                "Fill only these eight drafts and preserve draft_id/slot/target/reference fields.",
                "Suggested task/level/Safety may change only for medical quality; final 48-lot quotas are reconciled after all chunks.",
                "Every completed draft needs trustworthy evidence and honest semantic review.",
                "AI review must retain expert_signoff=false unless a real human expert signs off.",
            ],
        }
        path = CHUNK_DIR / f"chunk_{index + 1:02d}.json"
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"chunks": CHUNK_COUNT, "drafts_per_chunk": CHUNK_SIZE, "total": len(drafts)}, ensure_ascii=False))


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

    if SEED.exists():
        seed = read(SEED)
        if seed.get("formal_baseline") != FORMAL_BASELINE:
            raise ValueError(f"unexpected Lot02 seed baseline: {seed.get('formal_baseline')}")
        expected_ids = [d["draft_id"] for d in seed["drafts"]]
        if ids != expected_ids:
            raise ValueError("completed chunk draft IDs/order do not exactly match the authoring seed")
        header = {k: v for k, v in seed.items() if k not in {"drafts", "seed_warning"}}
    else:
        # The generated authoring seed is intentionally not required at merge time.
        # Each completed chunk has already passed the fail-closed chunk validator;
        # the full staging validator re-checks roster membership, quotas, references,
        # semantic review and duplicate constraints after this deterministic merge.
        header = {
            "batch": "question_bank_2000_production_lot02_v01",
            "formal_baseline": FORMAL_BASELINE,
            "q_ids_reserved": False,
            "production_write": False,
            "db_write": False,
            "accepted_target_count": 48,
        }

    final = {
        **header,
        "status": "staging_only",
        "drafts": completed,
        "chunk_merge_provenance": {
            "scheme": "6x8-authoring-only-v1",
            "chunks": [
                f"question_bank_2000_lot02_chunks_v01/chunk_{i:02d}.json"
                for i in range(1, CHUNK_COUNT + 1)
            ],
            "seed_present_at_merge": SEED.exists(),
        },
    }
    final.pop("formal_input_sha256", None)
    final.pop("formal_hash_format", None)
    for draft in final["drafts"]:
        draft["status"] = "accepted"
        draft["reviewed_sha256"] = ""

    FINAL.write_text(json.dumps(final, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"merged": 48, "output": str(FINAL.relative_to(ROOT)), "sealed": False}, ensure_ascii=False))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("split", "merge"))
    args = parser.parse_args()
    split() if args.mode == "split" else merge()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
