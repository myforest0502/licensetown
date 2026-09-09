import json
import shutil

from scripts import integrate_question_bank_2000_lot05 as integrator


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def test_lot05_integrator_dry_run_is_atomic_and_idempotent(tmp_path):
    target = tmp_path / "question_bank"
    shutil.copytree(integrator.BANK, target)
    before_canonical = (target / "knowledge_node_canonical_map.json").read_bytes()
    before_pairs = (target / "strong_different_question_pairs.json").read_bytes()

    integrator.integrate(target, integrator.STAGING)
    integrator.integrate(target, integrator.STAGING)

    manifest = read(target / "bank_manifest.json")
    assert manifest == {
        "bank_version": "2026-09-b19",
        "first_question_number": 1,
        "last_question_number": 1994,
        "question_count": 1994,
    }
    stores = [read(target / name) for name in (
        "questions.json", "answers.json", "explanations.json", "question_tags.json"
    )]
    expected = [f"Q{i}" for i in range(1, 1995)]
    assert all([row["id"] for row in store] == expected for store in stores)

    nodes = read(target / "knowledge_nodes.json")
    node_index = {row["knowledge_node_id"]: row for row in nodes}
    assert len(nodes) == len(node_index) == 1558
    assert all(f"KN{i:04d}" in node_index for i in range(1556, 1559))

    tags = {row["id"]: row for row in stores[3]}
    new_drafts = [
        (offset, row) for offset, row in enumerate(read(integrator.STAGING)["drafts"])
        if row["slot_type"] == "new_node"
    ]
    assert len(new_drafts) == 3
    assert [tags[f"Q{1954 + offset}"]["knowledge_node_id"] for offset, _ in new_drafts] == [
        "KN1556", "KN1557", "KN1558"
    ]
    assert (target / "knowledge_node_canonical_map.json").read_bytes() == before_canonical
    assert (target / "strong_different_question_pairs.json").read_bytes() == before_pairs
