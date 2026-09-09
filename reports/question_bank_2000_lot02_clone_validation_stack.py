"""Derive the Lot02 final validator/seal stack from the proven Lot01 stack.

This keeps the validated logic identical and changes only Lot-specific constants,
paths, IDs and version/range contracts. It is intentionally mechanical so later
lots can use the same pattern without hand-editing a large validator.
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"

REPLACEMENTS = [
    ("Lot01", "Lot02"),
    ("lot01", "lot02"),
    ("L01", "L02"),
    ("question_bank_2000_production_lot01_v01", "question_bank_2000_production_lot02_v01"),
    ("Q1-Q1761", "Q1-Q1809"),
    ("BASE_COUNT = 1761", "BASE_COUNT = 1809"),
    ('BASE_VERSION = "2026-09-b14"', 'BASE_VERSION = "2026-09-b15"'),
    ("INTEGRATED_START = 1762", "INTEGRATED_START = 1810"),
    ("INTEGRATED_END = 1809", "INTEGRATED_END = 1857"),
    ('INTEGRATED_VERSION = "2026-09-b15"', 'INTEGRATED_VERSION = "2026-09-b16"'),
    ("formal integrated count is below 1809", "formal integrated count is below 1857"),
    ("formal baseline count is not 1761", "formal baseline count is not 1809"),
    ("formal baseline range is not Q1-Q1761", "formal baseline range is not Q1-Q1809"),
    ("formal baseline version is not 2026-09-b14", "formal baseline version is not 2026-09-b15"),
    ("formal integrated version is not 2026-09-b15", "formal integrated version is not 2026-09-b16"),
    ("CATEGORY_QUOTA = {9:12,16:10,17:12,18:14}", "CATEGORY_QUOTA = {8:8,9:6,11:5,12:5,14:4,16:5,17:7,18:8}"),
    ("allocated_node_id = f\"KN{1539 + new_node_offset:04d}\"", "allocated_node_id = f\"KN{1543 + new_node_offset:04d}\""),
]


def transform(text: str) -> str:
    out = text
    for old, new in REPLACEMENTS:
        out = out.replace(old, new)
    return out


def clone(source_name: str, target_name: str) -> None:
    source = REPORTS / source_name
    target = REPORTS / target_name
    text = source.read_text(encoding="utf-8")
    output = transform(text)
    if output == text:
        raise ValueError(f"no Lot02 transformation occurred for {source_name}")
    target.write_text(output, encoding="utf-8")


def validate_generated_contract() -> None:
    validator = (REPORTS / "question_bank_2000_lot02_validate.py").read_text(encoding="utf-8")
    seal = (REPORTS / "question_bank_2000_lot02_seal.py").read_text(encoding="utf-8")
    required = [
        "Q1-Q1809",
        "BASE_COUNT = 1809",
        'BASE_VERSION = "2026-09-b15"',
        "INTEGRATED_START = 1810",
        "INTEGRATED_END = 1857",
        'INTEGRATED_VERSION = "2026-09-b16"',
        "CATEGORY_QUOTA = {8:8,9:6,11:5,12:5,14:4,16:5,17:7,18:8}",
        'allocated_node_id = f"KN{1543 + new_node_offset:04d}"',
        "question_bank_2000_lot02_targets_v01.json",
        "question_bank_2000_lot02_v01.json",
        "question_bank_2000_production_lot02_v01",
    ]
    missing = [token for token in required if token not in validator]
    if missing:
        raise ValueError(f"generated Lot02 validator missing contract tokens: {missing}")
    forbidden = [
        "Q1-Q1761",
        "BASE_COUNT = 1761",
        'BASE_VERSION = "2026-09-b14"',
        "INTEGRATED_START = 1762",
        "INTEGRATED_END = 1809",
        'INTEGRATED_VERSION = "2026-09-b15"',
        'allocated_node_id = f"KN{1539 + new_node_offset:04d}"',
        "question_bank_2000_lot01_targets_v01.json",
        "question_bank_2000_lot01_v01.json",
        "question_bank_2000_production_lot01_v01",
    ]
    leaked = [token for token in forbidden if token in validator]
    if leaked:
        raise ValueError(f"Lot01 contract leaked into generated Lot02 validator: {leaked}")
    if "question_bank_2000_lot02_validate" not in seal:
        raise ValueError("generated Lot02 seal does not import Lot02 validator")


def main() -> int:
    clone("question_bank_2000_lot01_validate.py", "question_bank_2000_lot02_validate.py")
    clone("question_bank_2000_lot01_seal.py", "question_bank_2000_lot02_seal.py")
    validate_generated_contract()
    print("Lot02 validator/seal stack generated from proven Lot01 stack")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
