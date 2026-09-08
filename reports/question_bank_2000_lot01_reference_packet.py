"""Build formal reference packets for any Lot01 authoring chunk.

Read-only against the formal Question Bank. No Q IDs or Node IDs are allocated.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BANK = ROOT / "data" / "question_bank"
CHUNK_DIR = ROOT / "staging" / "question_bank_2000_lot01_chunks_v01"
OUT_DIR = ROOT / "reports" / "question_bank_2000_lot01_reference_packets"


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def index(rows):
    return {str(r["id"]): r for r in rows}


def build(chunk_no: int) -> dict:
    chunk = read(CHUNK_DIR / f"chunk_{chunk_no:02d}.json")
    qids: list[str] = []
    for draft in chunk.get("drafts", []):
        for qid in draft.get("reference_question_ids", []):
            qid = str(qid)
            if qid not in qids:
                qids.append(qid)

    stores = {
        "question": index(read(BANK / "questions.json")),
        "answer": index(read(BANK / "answers.json")),
        "explanation": index(read(BANK / "explanations.json")),
        "tag": index(read(BANK / "question_tags.json")),
    }
    packet = []
    for qid in qids:
        missing = [name for name, rows in stores.items() if qid not in rows]
        if missing:
            raise ValueError(f"{qid} missing from formal stores: {missing}")
        packet.append({
            "qid": qid,
            "question": stores["question"][qid],
            "answer": stores["answer"][qid],
            "explanation": stores["explanation"][qid],
            "tag": stores["tag"][qid],
        })
    return {"chunk": chunk_no, "formal_baseline": "Q1-Q1761", "references": packet}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("chunk", type=int, choices=range(1, 7))
    args = parser.parse_args()
    payload = build(args.chunk)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / f"chunk_{args.chunk:02d}.json"
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"chunk": args.chunk, "references": len(payload["references"]), "output": str(out.relative_to(ROOT))}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
