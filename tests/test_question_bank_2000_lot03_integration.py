import json
import shutil
from pathlib import Path

from scripts import integrate_question_bank_2000_lot03 as integrator

ROOT = Path(__file__).parents[1]
BANK = ROOT / "data" / "question_bank"
STAGING = ROOT / "staging" / "question_bank_2000_lot03_v01.json"


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def test_lot03_integrator_dry_run_is_atomic_and_idempotent(tmp_path):
    target = tmp_path / "question_bank"
    shutil.copytree(BANK, target)
    before_canonical = (target / "knowledge_node_canonical_map.json").read_bytes()
    before_pairs = (target / "strong_different_question_pairs.json").read_bytes()

    integrator.integrate(target, STAGING)
    integrator.integrate(target, STAGING)

    manifest = read(target / "bank_manifest.json")
    assert manifest["question_count"] == manifest["last_question_number"] == 1905
    assert manifest["bank_version"] == "2026-09-b17"

    stores = [read(target / name) for name in ("questions.json", "answers.json", "explanations.json", "question_tags.json")]
    expected = [f"Q{i}" for i in range(1, 1906)]
    assert all([row["id"] for row in store] == expected for store in stores)

    nodes = read(target / "knowledge_nodes.json")
    node_index = {row["knowledge_node_id"]: row for row in nodes}
    assert len(nodes) == len(node_index) == 1551
    assert all(f"KN{i:04d}" in node_index for i in range(1547, 1552))

    tags = {row["id"]: row for row in stores[3]}
    assert [tags[f"Q{i}"]["knowledge_node_id"] for i in range(1901, 1906)] == [f"KN{i:04d}" for i in range(1547, 1552)]

    # Existing-node Lot03 additions must create a different metadata demand.
    staging = read(STAGING)
    existing = [row for row in staging["drafts"] if row["slot_type"] != "new_node"]
    assert len(existing) == 43
    for offset, draft in enumerate(staging["drafts"]):
        if draft["slot_type"] == "new_node":
            continue
        qid = f"Q{1858 + offset}"
        demand = (tags[qid]["task"], tags[qid]["primary_ability"])
        prior = {(x["task"], x["primary_ability"]) for x in draft["existing_demands"]}
        assert demand not in prior

    assert (target / "knowledge_node_canonical_map.json").read_bytes() == before_canonical
    assert (target / "strong_different_question_pairs.json").read_bytes() == before_pairs
