"""Run one anonymous Production Field Progress audit; never writes to the DB."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from database import database_is_available
from progress_shadow_audit import get_user_progress_shadow_audit


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--user-id", default=os.getenv("SHADOW_AUDIT_USER_ID"))
    parser.add_argument("--output")
    args = parser.parse_args()
    if not database_is_available():
        print(json.dumps({
            "production_read_only_executed": False,
            "reason": "DATABASE_URL is unavailable",
            "db_write_count": 0,
        }, ensure_ascii=False, indent=2))
        return 0
    if not args.user_id:
        print(json.dumps({
            "production_read_only_executed": False,
            "reason": "Provide --user-id or SHADOW_AUDIT_USER_ID",
            "db_write_count": 0,
        }, ensure_ascii=False, indent=2))
        return 0
    report = get_user_progress_shadow_audit(args.user_id)
    report["production_read_only_executed"] = True
    report["db_write_count"] = 0
    payload = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(payload + "\n", encoding="utf-8")
    print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
