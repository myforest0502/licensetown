"""PT data/module canonicalization under licensetown.pt."""

import importlib
from pathlib import Path

MODULES = (
    "question_bank",
    "question_equivalence",
    "knowledge_node_canonical",
    "knowledge_node_relations",
    "knowledge_node_repair_evidence",
    "pilot_diagnostics",
)

def test_legacy_pt_data_modules_are_canonical():
    for name in MODULES:
        legacy = importlib.import_module(name)
        canonical = importlib.import_module(f"licensetown.pt.{name}")
        assert legacy is canonical

def test_canonical_question_bank_uses_pt_data_copy():
    qb = importlib.import_module("licensetown.pt.question_bank")
    expected = Path(qb.__file__).resolve().parent / "data" / "question_bank"
    assert qb.QUESTION_BANK_DIR == expected
    assert (expected / "bank_manifest.json").is_file()
    assert qb.question_count() == 2233
