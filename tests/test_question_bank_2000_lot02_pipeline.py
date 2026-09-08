import hashlib
import json
from collections import Counter
from pathlib import Path

from reports import question_bank_2000_lot02_assignment_v01 as assignment
from reports import question_bank_2000_lot02_build_seed as seed
from reports import question_bank_2000_lot02_build_template as template
from reports import question_bank_2000_lot02_chunks as chunks
from reports import question_bank_2000_lot02_clone_validation_stack as validation_stack
from reports import question_bank_2000_lot02_targets_v01 as targets

ROOT = Path(__file__).parents[1]
BANK = ROOT / "data" / "question_bank"
PROTECTED = (
    "questions.json",
    "answers.json",
    "explanations.json",
    "question_tags.json",
    "knowledge_nodes.json",
    "bank_manifest.json",
    "schema/question_bank_schema_v1.json",
    "knowledge_node_canonical_map.json",
    "strong_different_question_pairs.json",
)


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_lot02_preparation_pipeline_is_quota_exact_and_formal_read_only():
    before = {name: digest(BANK / name) for name in PROTECTED}

    targets.main()
    assignment.main()
    template.main()
    seed.main()
    chunks.split()
    validation_stack.main()

    roster = read(ROOT / "reports" / "question_bank_2000_lot02_targets_v01.json")
    assigned = read(ROOT / "reports" / "question_bank_2000_lot02_assignment_v01.json")
    authoring_seed = read(ROOT / "staging" / "question_bank_2000_lot02_authoring_seed_v01.json")

    assert roster["formal_baseline"] == "Q1-Q1809"
    assert roster["required_existing_targets"] == 44
    assert roster["required_new_nodes"] == 4
    assert roster["required_total_questions"] == 48
    assert len(roster["existing_node_targets"]) == 44
    assert len({row["canonical_node_id"] for row in roster["existing_node_targets"]}) == 44
    assert Counter(row["slot_type"] for row in roster["existing_node_targets"]) == Counter({
        "singleton_second": 32,
        "multi_reinforcement": 12,
    })
    assert Counter(int(row["category_small"]) for row in roster["existing_node_targets"]) + Counter(
        {int(row["category_small"]): int(row["count"]) for row in roster["new_node_reservations"]}
    ) == Counter({8: 8, 9: 6, 11: 5, 12: 5, 14: 4, 16: 5, 17: 7, 18: 8})

    assert assigned["formal_baseline"] == "Q1-Q1809"
    assert Counter(row["suggested_task"] for row in assigned["assignments"]) == Counter({
        "assessment_selection": 9,
        "device_selection": 2,
        "fact_recall": 1,
        "finding_interpretation": 14,
        "functional_goal_decision": 4,
        "intervention_selection": 9,
        "prognosis_prediction": 3,
        "safety_priority": 6,
    })
    assert Counter(row["suggested_level"] for row in assigned["assignments"]) == Counter({1: 1, 2: 16, 3: 20, 4: 11})
    assert sum(row["suggested_safety"] in {"moderate", "critical"} for row in assigned["assignments"]) == 12
    assert assigned["structurally_distinct_existing_assignments"] == 44

    assert authoring_seed["formal_baseline"] == "Q1-Q1809"
    assert len(authoring_seed["drafts"]) == 48
    assert len({row["draft_id"] for row in authoring_seed["drafts"]}) == 48
    assert authoring_seed["q_ids_reserved"] is False
    assert authoring_seed["production_write"] is False
    assert authoring_seed["db_write"] is False

    for index in range(1, 7):
        chunk = read(ROOT / "staging" / "question_bank_2000_lot02_chunks_v01" / f"chunk_{index:02d}.json")
        assert chunk["formal_baseline"] == "Q1-Q1809"
        assert chunk["status"] == "authoring_chunk"
        assert len(chunk["drafts"]) == 8
        assert chunk["q_ids_reserved"] is False
        assert chunk["production_write"] is False
        assert chunk["db_write"] is False

    assert (ROOT / "reports" / "question_bank_2000_lot02_validate.py").exists()
    assert (ROOT / "reports" / "question_bank_2000_lot02_seal.py").exists()

    after = {name: digest(BANK / name) for name in PROTECTED}
    assert after == before
