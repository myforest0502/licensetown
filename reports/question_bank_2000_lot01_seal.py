"""Seal a fully authored and reviewed Lot01 staging file without approving content itself."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from reports.question_bank_2000_lot01_validate import (
    BANK,
    PROTECTED,
    STAGING,
    build_report,
    draft_fingerprint,
    file_fingerprint,
)


def main() -> int:
    if not STAGING.exists():
        raise SystemExit(f"missing authored staging file: {STAGING}")
    payload = json.loads(STAGING.read_text(encoding="utf-8-sig"))

    # Pre-seal validation checks content, quotas, references and semantic-review decisions.
    # It deliberately does not infer or change those decisions.
    report = build_report(payload, require_seals=False)
    if report["hard_errors"]:
        print(json.dumps(report, ensure_ascii=False, indent=2))
        raise SystemExit("Lot01 cannot be sealed while pre-seal validation has hard errors")

    payload["formal_hash_format"] = "sha256-lf-normalized-v1"
    payload["formal_input_sha256"] = {
        name: file_fingerprint(BANK / name) for name in PROTECTED
    }
    for draft in payload["drafts"]:
        draft["reviewed_sha256"] = draft_fingerprint(draft)

    STAGING.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    final_report = build_report(payload, require_seals=True)
    if final_report["hard_errors"]:
        print(json.dumps(final_report, ensure_ascii=False, indent=2))
        raise SystemExit("Lot01 sealing produced an invalid final staging state")
    print(json.dumps({
        "sealed": True,
        "accepted_count": final_report["accepted_count"],
        "structural_strong_formations": final_report["structural_strong_formations"],
        "warnings": final_report["warnings"],
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
