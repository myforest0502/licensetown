"""Generate the deterministic ⑩-C human-review artifact."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from alternative_repair_confirmation_shadow import build_shadow_review_artifact


OUTPUT = ROOT / "data" / "question_bank" / "alternative_repair_shadow_review_v0.1.json"


def main() -> int:
    OUTPUT.write_text(
        json.dumps(build_shadow_review_artifact(), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(OUTPUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
