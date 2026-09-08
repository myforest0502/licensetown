"""Audit any completed Lot02 authoring chunk against all formal Q1-Q1809 stems."""
from __future__ import annotations

import argparse
import json
import re
import unicodedata
from difflib import SequenceMatcher
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BANK = ROOT / "data" / "question_bank"
CHUNK_DIR = ROOT / "staging" / "question_bank_2000_lot02_chunks_v01"
OUT_DIR = ROOT / "reports" / "question_bank_2000_lot02_similarity_audits"
NEAR = 0.65
HARD = 0.78


def normalize(text: str) -> str:
    value = unicodedata.normalize("NFKC", str(text or "")).lower()
    return re.sub(r"[^0-9a-zぁ-んァ-ヶ一-龠々ー]+", "", value)


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def audit(chunk_no: int) -> dict:
    formal = read(BANK / "questions.json")
    if max(int(row["id"][1:]) for row in formal) != 1809:
        raise ValueError("Lot02 similarity audit requires formal Q1-Q1809")
    chunk = read(CHUNK_DIR / f"chunk_{chunk_no:02d}.json")
    if chunk.get("status") != "completed_chunk":
        raise ValueError(f"Chunk{chunk_no:02d} must be completed before similarity audit")
    if chunk.get("formal_baseline") != "Q1-Q1809":
        raise ValueError("Lot02 chunk formal baseline mismatch")
    formal_norm = [(q["id"], q.get("question_text", ""), normalize(q.get("question_text", ""))) for q in formal]
    results = []
    exact_total = 0
    hard_total = 0
    near_total = 0
    for draft in chunk["drafts"]:
        did = draft["draft_id"]
        stem = draft["question_text"]
        norm = normalize(stem)
        ranked = []
        for qid, qtext, qnorm in formal_norm:
            if not qnorm:
                continue
            score = SequenceMatcher(None, norm, qnorm, autojunk=False).ratio()
            ranked.append((score, qid, qtext))
        ranked.sort(reverse=True)
        top = [{"qid": qid, "score": round(score, 6), "question_text": qtext} for score, qid, qtext in ranked[:10]]
        exact = [x for x in top if x["score"] == 1.0]
        hard = [x for x in top if x["score"] >= HARD]
        near = [x for x in top if x["score"] >= NEAR]
        exact_total += len(exact)
        hard_total += len(hard)
        near_total += len(near)
        results.append({
            "draft_id": did,
            "reference_question_ids": draft.get("reference_question_ids", []),
            "exact": exact,
            "hard_near": hard,
            "near": near,
            "top10": top,
        })
    return {
        "formal_baseline": "Q1-Q1809",
        "chunk": chunk_no,
        "thresholds": {"near": NEAR, "hard_near": HARD},
        "exact_total": exact_total,
        "hard_near_total": hard_total,
        "near_total": near_total,
        "results": results,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("chunk", type=int, choices=range(1, 7))
    args = parser.parse_args()
    payload = audit(args.chunk)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / f"chunk_{args.chunk:02d}.json"
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"chunk": args.chunk, "exact_total": payload["exact_total"], "hard_near_total": payload["hard_near_total"], "near_total": payload["near_total"], "output": str(out.relative_to(ROOT))}, ensure_ascii=False))
    if payload["exact_total"]:
        raise SystemExit("exact formal duplicate detected")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
