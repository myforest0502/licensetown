from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BANK_DIR = ROOT / "data" / "question_bank"
MANIFEST = BANK_DIR / "bank_manifest.json"
SCHEMA = BANK_DIR / "schema" / "question_bank_schema_v1.json"


def check_schema_manifest() -> dict[str, object]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8-sig"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8-sig"))
    first = int(manifest["first_question_number"])
    last = int(manifest["last_question_number"])
    count = int(manifest["question_count"])
    if count != last - first + 1:
        raise ValueError("manifest range/count mismatch")
    for name in ("questions", "answers", "explanations", "question_tags"):
        item = schema["properties"][name]
        if item.get("minItems") != count or item.get("maxItems") != count:
            raise ValueError(f"{name}: schema count is stale relative to manifest")
    pattern = schema["$defs"]["qid"]["pattern"]
    if re.fullmatch(pattern, f"Q{first}") is None or re.fullmatch(pattern, f"Q{last}") is None:
        raise ValueError("schema QID pattern does not include declared range")
    if re.fullmatch(pattern, f"Q{last + 1}") is not None:
        raise ValueError("schema QID pattern accepts ID above declared range")
    return {
        "bank_version": manifest["bank_version"],
        "first_question_number": first,
        "last_question_number": last,
        "question_count": count,
    }


def main() -> int:
    print(json.dumps(check_schema_manifest(), ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
