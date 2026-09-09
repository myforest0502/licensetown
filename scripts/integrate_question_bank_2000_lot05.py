"""Atomically integrate sealed Question Bank 2000 Lot05 as Q1954-Q1994."""
from __future__ import annotations

from pathlib import Path

from reports import question_bank_2000_lot05_validate as validator
from scripts import integrate_question_bank_2000_lot04 as base

ROOT = Path(__file__).resolve().parents[1]
BANK = ROOT / "data" / "question_bank"
STAGING = ROOT / "staging" / "question_bank_2000_lot05_v01.json"

def integrate(bank_dir: Path = BANK, staging_path: Path = STAGING) -> None:
    settings = {
        "STAGING": STAGING,
        "build_report": validator.build_report,
        "draft_fingerprint": validator.draft_fingerprint,
        "file_fingerprint": validator.file_fingerprint,
        "START_Q": 1954,
        "END_Q": 1994,
        "EXPECTED_DRAFT_COUNT": 41,
        "EXPECTED_BASE_END": 1953,
        "TARGET_VERSION": "2026-09-b19",
        "START_NODE": 1556,
        "END_NODE": 1558,
        "NEW_NODE_PREREQUISITES": {
            "L05-C1-N01": ["下肢末梢神経の障害部位は、感覚分布と運動・反射所見を組み合わせて局在する。"],
            "L05-C2-N01": ["動脈血酸素分圧の変化は化学受容器を介して呼吸調節へ影響する。"],
            "L05-C7-N01": ["組織内沈着物の同定には、対象物質に応じた特殊染色と観察法を用いる。"],
        },
        "QID_PATTERN": r"^Q(?:[1-9]|[1-9][0-9]{1,2}|1[0-8][0-9]{2}|19[0-8][0-9]|199[0-4])$",
    }
    previous = {name: getattr(base, name) for name in settings}
    try:
        for name, value in settings.items():
            setattr(base, name, value)
        base.integrate(bank_dir, staging_path)
    finally:
        for name, value in previous.items():
            setattr(base, name, value)


if __name__ == "__main__":
    integrate()
