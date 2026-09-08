"""Audit completed Lot01 Chunk01 stems against all formal Q1-Q1761 stems."""
from __future__ import annotations

import json
from difflib import SequenceMatcher
from pathlib import Path

from reports.question_bank_2000_lot01_validate import normalize

ROOT = Path(__file__).resolve().parents[1]
BANK = ROOT / "data" / "question_bank"
CHUNK = ROOT / "staging" / "question_bank_2000_lot01_chunks_v01" / "chunk_01.json"
OUT = ROOT / "reports" / "question_bank_2000_lot01_chunk01_similarity_audit.json"
NEAR = 0.65
HARD = 0.78


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def main() -> int:
    formal = read(BANK / "questions.json")
    chunk = read(CHUNK)
    if chunk.get("status") != "completed_chunk":
        raise SystemExit("Chunk01 must be completed before similarity audit")
    formal_norm = [(q["id"], q.get("question_text", ""), normalize(q.get("question_text", ""))) for q in formal]
    results = []
    hard_total = 0
    exact_total = 0
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
        top = [
            {"qid": qid, "score": round(score, 6), "question_text": qtext}
            for score, qid, qtext in ranked[:10]
        ]
        exact = [x for x in top if x["score"] == 1.0]
        hard = [x for x in top if x["score"] >= HARD]
        near = [x for x in top if x["score"] >= NEAR]
        exact_total += len(exact)
        hard_total += len(hard)
        results.append({
            "draft_id": did,
            "reference_question_ids": draft.get("reference_question_ids", []),
            "exact": exact,
            "hard_near": hard,
            "near": near,
            "top10": top,
        })
    payload = {
        "formal_baseline": "Q1-Q1761",
        "chunk": 1,
        "thresholds": {"near": NEAR, "hard_near": HARD},
        "exact_total": exact_total,
        "hard_near_total": hard_total,
        "results": results,
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"exact_total": exact_total, "hard_near_total": hard_total, "output": str(OUT.relative_to(ROOT))}, ensure_ascii=False))
    if exact_total:
        raise SystemExit("exact formal duplicate detected")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
