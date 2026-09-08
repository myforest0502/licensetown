"""Clone the proven Lot03 validation scaffold into Lot04 with fail-closed substitutions.

This prepares infrastructure only. It does not author questions, seal staging, allocate
formal Q IDs, or mutate the formal Question Bank.
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PAIRS = [
    ("lot03", "lot04"), ("Lot03", "Lot04"), ("LOT03", "LOT04"),
    ("L03", "L04"), ("Q1-Q1857", "Q1-Q1905"),
]

FILES = [
    ("reports/question_bank_2000_lot03_chunk_validate.py", "reports/question_bank_2000_lot04_chunk_validate.py"),
    ("reports/question_bank_2000_lot03_chunks.py", "reports/question_bank_2000_lot04_chunks.py"),
    ("reports/question_bank_2000_lot03_similarity_audit.py", "reports/question_bank_2000_lot04_similarity_audit.py"),
    ("reports/question_bank_2000_lot03_seal.py", "reports/question_bank_2000_lot04_seal.py"),
    ("reports/question_bank_2000_lot03_validate.py", "reports/question_bank_2000_lot04_validate.py"),
]

# Lot04 structural quotas that differ from Lot03. Apply only to copied Lot04 files.
EXACT_REPLACEMENTS = [
    ("singleton_second\": 30", "singleton_second\": 27"),
    ("multi_reinforcement\": 13", "multi_reinforcement\": 17"),
    ("new_node\": 5", "new_node\": 4"),
    ("required_strong_formations\": 41", "required_strong_formations\": 37"),
    ("safety_moderate_or_critical\": 13", "safety_moderate_or_critical\": 12"),
]


def transform(text: str) -> str:
    out = text
    for old, new in PAIRS:
        out = out.replace(old, new)
    for old, new in EXACT_REPLACEMENTS:
        out = out.replace(old, new)
    return out


def main() -> int:
    written=[]
    for src_name,dst_name in FILES:
        src=ROOT/src_name; dst=ROOT/dst_name
        if not src.exists(): raise FileNotFoundError(src)
        text=transform(src.read_text(encoding="utf-8"))
        if "lot03" in text or "Lot03" in text or "L03" in text:
            raise ValueError(f"unconverted Lot03 marker in {dst_name}")
        dst.write_text(text,encoding="utf-8")
        written.append(dst_name)
    print("Lot04 scaffold cloned:")
    print("\n".join(written))
    return 0

if __name__=="__main__": raise SystemExit(main())
