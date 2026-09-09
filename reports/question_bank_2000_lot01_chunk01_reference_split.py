"""Split the Chunk01 reference packet into one small file per formal Q for review."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "reports" / "question_bank_2000_lot01_chunk01_reference_packet.json"
OUT = ROOT / "reports" / "question_bank_2000_lot01_chunk01_refs"


def main() -> int:
    rows = json.loads(SRC.read_text(encoding="utf-8-sig"))
    OUT.mkdir(parents=True, exist_ok=True)
    for row in rows:
        qid = str(row["qid"])
        (OUT / f"{qid}.json").write_text(json.dumps(row, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"files": len(rows), "out": str(OUT.relative_to(ROOT))}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
