"""Split a generated Lot01 formal-reference packet into one file per formal Q."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKETS = ROOT / "reports" / "question_bank_2000_lot01_reference_packets"
OUT_ROOT = ROOT / "reports" / "question_bank_2000_lot01_reference_items"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("chunk", type=int, choices=range(1, 7))
    args = parser.parse_args()
    src = PACKETS / f"chunk_{args.chunk:02d}.json"
    payload = json.loads(src.read_text(encoding="utf-8-sig"))
    out = OUT_ROOT / f"chunk_{args.chunk:02d}"
    out.mkdir(parents=True, exist_ok=True)
    for row in payload["references"]:
        (out / f"{row['qid']}.json").write_text(json.dumps(row, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"chunk": args.chunk, "files": len(payload["references"]), "out": str(out.relative_to(ROOT))}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
