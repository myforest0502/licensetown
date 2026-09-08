"""Extract the eight formal reference packets needed to author Lot01 chunk 01."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BANK = ROOT / "data" / "question_bank"
OUT = ROOT / "reports" / "question_bank_2000_lot01_chunk01_reference_packet.json"
QIDS = ["Q561", "Q566", "Q582", "Q621", "Q646", "Q695", "Q789", "Q839"]


def read(name: str):
    return json.loads((BANK / name).read_text(encoding="utf-8-sig"))


def index(rows):
    return {str(r["id"]): r for r in rows}


def main() -> int:
    stores = {
        "question": index(read("questions.json")),
        "answer": index(read("answers.json")),
        "explanation": index(read("explanations.json")),
        "tag": index(read("question_tags.json")),
    }
    packet = []
    for qid in QIDS:
        packet.append({
            "qid": qid,
            "question": stores["question"][qid],
            "answer": stores["answer"][qid],
            "explanation": stores["explanation"][qid],
            "tag": stores["tag"][qid],
        })
    OUT.write_text(json.dumps(packet, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"references": len(packet), "qids": QIDS, "output": str(OUT.relative_to(ROOT))}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
