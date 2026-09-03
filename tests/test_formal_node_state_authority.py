"""Architecture guardrails for Issue #103.

`question_attempts` + the pure state-transition engine are the formal truth.
`database.user_node_state` remains a legacy/partial persistence boundary and must
not leak into runtime learning-state decisions.
"""

from __future__ import annotations

import ast
from pathlib import Path

import field_evidence
import pass_readiness


ROOT = Path(__file__).resolve().parents[1]


def _runtime_python_files():
    for path in ROOT.rglob("*.py"):
        relative = path.relative_to(ROOT)
        if relative.parts[0] in {"tests", "scripts", ".venv", "venv"}:
            continue
        if relative.as_posix() == "database.py":
            # The legacy table is owned only by the persistence boundary.
            continue
        yield path


def _legacy_state_references(path: Path):
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    findings = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and node.id == "get_user_node_states":
            findings.append((node.lineno, "get_user_node_states name"))
        elif isinstance(node, ast.Attribute) and node.attr == "get_user_node_states":
            findings.append((node.lineno, "get_user_node_states attribute"))
        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            normalized = " ".join(node.value.lower().split())
            if "from user_node_state" in normalized or "join user_node_state" in normalized:
                findings.append((getattr(node, "lineno", 0), "direct user_node_state SQL read"))
    return findings


def test_no_runtime_consumer_reads_legacy_persisted_node_state():
    violations = {}
    for path in _runtime_python_files():
        findings = _legacy_state_references(path)
        if findings:
            violations[path.relative_to(ROOT).as_posix()] = findings
    assert violations == {}, (
        "Formal runtime learning state must come from question_attempts + pure "
        f"derivation, not persisted user_node_state: {violations}"
    )


def test_evidence_and_readiness_declare_pure_authoritative_state_source(monkeypatch):
    attempts = []
    evidence = field_evidence.build_field_evidence(attempts)
    progress = {
        "overall": {
            "total_unique_canonical_nodes": 0,
            "touched_unique_canonical_nodes": 0,
            "state_counts": {},
            "overall_progress_score": 0.0,
        }
    }

    # Keep this regression focused on source authority, not catalog thresholds.
    monkeypatch.setattr(pass_readiness, "_ABILITY_OPPORTUNITIES", {name: set() for name in pass_readiness.ABILITIES})
    monkeypatch.setattr(
        pass_readiness,
        "build_formal_context",
        lambda attempts, field_evidence, as_of=None: {"active_by_node": {}, "active_field_facts": {}},
    )
    result = pass_readiness.build_pass_readiness(
        attempts,
        field_evidence=evidence,
        progress=progress,
    )
    assert result["authoritative_attempt_source"] == "question_attempts"
    assert result["authoritative_node_state_source"] == "pure_derive_all_user_node_states"
