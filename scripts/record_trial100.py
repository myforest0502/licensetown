"""Record one real paper Trial100 result into the explicit Trial100 store.

Usage example:
python scripts/record_trial100.py --user-id USER --date 2026-09-20 \
  --correct 78 --duration 155 --source trial100-2026-09-a

This script never infers pass/supportive status from score.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from trial100_store import save_trial100_record


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description="Record a paper Trial100 result")
    result.add_argument("--user-id", required=True)
    result.add_argument("--date", required=True, dest="test_date")
    result.add_argument("--correct", required=True, type=int, dest="correct_count")
    result.add_argument("--duration", type=int, dest="duration_minutes")
    result.add_argument("--source", required=True, dest="source_version")
    result.add_argument("--incomplete", action="store_true")
    result.add_argument("--recorded-by", default="developer-cli")
    return result


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    record = save_trial100_record(
        {
            "user_id": args.user_id,
            "test_date": args.test_date,
            "source_version": args.source_version,
            "total_questions": 100,
            "correct_count": args.correct_count,
            "completion_status": "incomplete" if args.incomplete else "completed",
            "duration_minutes": args.duration_minutes,
            "supportive": False,
        },
        recorded_by=args.recorded_by,
    )
    print(json.dumps(record, ensure_ascii=False, default=str, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
