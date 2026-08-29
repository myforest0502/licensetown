import json
from pathlib import Path

from scripts.build_same_node_candidate_expansion_v01 import (
    ALLOWED_ACTIONS,
    OUTPUT_AUDIT,
    OUTPUT_JSON,
    build_audit,
    build_candidates,
)


ROOT = Path(__file__).resolve().parents[1]
BANK = ROOT / "data" / "question_bank"


def load(name):
    return json.loads((BANK / name).read_text(encoding="utf-8-sig"))


def test_candidates_are_complete_unique_and_capped():
    candidates = build_candidates()
    assert 0 < len(candidates) <= 50
    assert len({item["candidate_id"] for item in candidates}) == len(candidates)
    assert len({frozenset(item["node_ids"]) for item in candidates}) == len(candidates)
    assert all(len(item["node_ids"]) == len(item["question_ids"]) == 2 for item in candidates)
    assert all(item["recommended_action"] in ALLOWED_ACTIONS for item in candidates)
    assert all(item["confidence"] in {"high", "medium", "low"} for item in candidates)


def test_all_node_and_question_references_exist():
    candidates = build_candidates()
    node_ids = {item["knowledge_node_id"] for item in load("knowledge_nodes.json")}
    question_ids = {item["id"] for item in load("questions.json")}
    assert all(set(item["node_ids"]) <= node_ids for item in candidates)
    assert all(set(item["question_ids"]) <= question_ids for item in candidates)


def test_existing_canonical_and_relation_pairs_are_excluded():
    candidates = {frozenset(item["node_ids"]) for item in build_candidates()}
    canonical = {
        frozenset([item["canonical_node_id"], alias])
        for item in load("knowledge_node_canonical_map.json")
        for alias in item["alias_node_ids"]
    }
    relations = {
        frozenset([item["source_node_id"], item["target_node_id"]])
        for item in load("knowledge_node_relations.json")
    }
    assert candidates.isdisjoint(canonical)
    assert candidates.isdisjoint(relations)


def test_high_same_node_records_have_explicit_repair_suitability():
    high_same = [
        item for item in build_candidates()
        if item["recommended_action"] == "SAME_NODE" and item["confidence"] == "high"
    ]
    assert high_same
    assert all("医学教育的に妥当" in item["repair_confirmation_suitability"] for item in high_same)


def test_committed_outputs_match_builder():
    assert json.loads(OUTPUT_JSON.read_text(encoding="utf-8")) == build_candidates()
    assert OUTPUT_AUDIT.read_text(encoding="utf-8") == build_audit(build_candidates())
