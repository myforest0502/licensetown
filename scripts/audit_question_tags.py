"""Generate a deterministic static audit for question_tags.json.

This script is read-only with respect to the Question Bank. It only writes the
requested report file and never changes question/tag content.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


DEFAULT_SOURCE = Path("data/question_bank/question_tags.json")
DEFAULT_REPORT = Path("data/question_bank/question_tags_audit.txt")
COUNT_FIELDS = (
    "tag_version",
    "tag_status",
    "task",
    "primary_ability",
    "secondary_ability",
    "level",
    "safety",
    "source",
)


def _qid_number(value: Any) -> int | None:
    text = str(value or "")
    if not text.startswith("Q") or not text[1:].isdigit():
        return None
    return int(text[1:])


def build_audit(records: list[dict[str, Any]], expected_count: int | None = None) -> str:
    ids = [str(item.get("id") or "") for item in records]
    id_counts = Counter(ids)
    valid_numbers = [_qid_number(value) for value in ids]
    invalid_ids = sorted(value for value, number in zip(ids, valid_numbers) if number is None)
    numbers = sorted(number for number in valid_numbers if number is not None)

    duplicates = sorted(value for value, count in id_counts.items() if value and count > 1)
    max_number = max(numbers, default=0)
    expected_max = expected_count if expected_count is not None else max_number
    missing = [f"Q{number}" for number in range(1, expected_max + 1) if f"Q{number}" not in id_counts]

    errors: list[str] = []
    if invalid_ids:
        errors.append(f"invalid_ids={','.join(invalid_ids)}")
    if expected_count is not None and len(records) != expected_count:
        errors.append(f"record_count_expected_{expected_count}_actual_{len(records)}")
    if max_number and max_number != expected_max:
        errors.append(f"max_q_expected_Q{expected_max}_actual_Q{max_number}")

    if numbers:
        q_range = f"Q{min(numbers)}-Q{max(numbers)}"
    else:
        q_range = "none"

    lines = [
        "LicenseTown question_tags.json audit",
        f"source: {DEFAULT_SOURCE.as_posix()}",
        f"records: {len(records)}",
        f"Q range: {q_range}",
        f"duplicates: {len(duplicates)}",
        f"missing: {len(missing)}",
        f"errors: {len(errors)}",
    ]

    if duplicates:
        lines.append(f"duplicate_ids: {', '.join(duplicates)}")
    if missing:
        lines.append(f"missing_ids: {', '.join(missing)}")
    if errors:
        lines.extend(f"error_detail: {item}" for item in errors)

    for field in COUNT_FIELDS:
        counts = Counter(item.get(field) for item in records)
        lines.extend(("", f"{field}:"))
        for key in sorted(counts, key=lambda value: (value is None, str(value))):
            label = "null" if key is None else str(key)
            lines.append(f"  {label}: {counts[key]}")

    return "\n".join(lines) + "\n"


def load_records(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list) or not all(isinstance(item, dict) for item in payload):
        raise ValueError("question_tags.json must contain a list of objects")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--expected-count", type=int, default=None)
    args = parser.parse_args()

    records = load_records(args.source)
    report = build_audit(records, expected_count=args.expected_count)
    args.output.write_text(report, encoding="utf-8")
    print(report, end="")

    failure_markers = (
        "duplicates: 0\n",
        "missing: 0\n",
        "errors: 0\n",
    )
    return 0 if all(marker in report for marker in failure_markers) else 1


if __name__ == "__main__":
    raise SystemExit(main())
