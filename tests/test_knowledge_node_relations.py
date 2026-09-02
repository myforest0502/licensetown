import copy
import json
from pathlib import Path

import pytest

from knowledge_node_relations import (
    KnowledgeNodeRelationValidationError,
    get_node_merge_candidates,
    get_node_relations,
    get_reviewed_node_relations,
    load_node_relation_data,
    validate_merge_candidates,
    validate_node_relations,
)
from question_bank import get_question_tag, question_count


BANK_DIR = Path(__file__).parents[1] / "data" / "question_bank"


def _formal_ids():
    nodes = json.loads((BANK_DIR / "knowledge_nodes.json").read_text(encoding="utf-8-sig"))
    questions = json.loads((BANK_DIR / "questions.json").read_text(encoding="utf-8-sig"))
    return (
        {node["knowledge_node_id"] for node in nodes},
        {question["id"] for question in questions},
    )


def test_formal_relation_and_merge_candidate_json_load():
    relations, candidates = load_node_relation_data()
    assert len(relations) == 13
    assert len(candidates) == 5
    assert {item["relation_type"] for item in relations} == {"PREREQUISITE", "TRANSFER"}
    assert sum(item["relation_type"] == "PREREQUISITE" for item in relations) == 12
    assert sum(item["relation_type"] == "TRANSFER" for item in relations) == 1


def test_relation_ids_references_enums_direction_and_duplicates_are_valid():
    node_ids, question_ids = _formal_ids()
    relations = get_node_relations()
    validate_node_relations(relations, node_ids, question_ids)
    assert len({item["relation_id"] for item in relations}) == len(relations)
    assert all(item["source_node_id"] != item["target_node_id"] for item in relations)


@pytest.mark.parametrize("mutation", [
    lambda records: records[0].update(relation_id="bad"),
    lambda records: records[0].update(relation_type="SAME_NODE"),
    lambda records: records[0].update(source_node_id="KN9999"),
    lambda records: records[0].update(target_node_id=records[0]["source_node_id"]),
    lambda records: records[0].update(confidence="certain"),
    lambda records: records[0].update(review_status="automatic"),
    lambda records: records[0].update(verification_role="promote_state"),
    lambda records: records[0].update(source_question_ids=["Q9999"]),
    lambda records: records.append(copy.deepcopy(records[0])),
])
def test_invalid_relation_data_is_rejected(mutation):
    node_ids, question_ids = _formal_ids()
    records = get_node_relations()
    mutation(records)
    with pytest.raises(KnowledgeNodeRelationValidationError):
        validate_node_relations(records, node_ids, question_ids)


def test_formal_filter_excludes_medium_pending_transfer():
    reviewed = get_reviewed_node_relations()
    assert len(reviewed) == 12
    assert all(item["relation_type"] == "PREREQUISITE" for item in reviewed)
    assert all(item["confidence"] == "high" for item in reviewed)
    assert "KNR0004" not in {item["relation_id"] for item in reviewed}


def test_expansion_relations_are_formal_and_held_pairs_are_absent():
    relations = get_node_relations()
    reviewed = get_reviewed_node_relations()
    expansion_ids = {f"KNR{number:04d}" for number in range(5, 14)}
    assert expansion_ids <= {item["relation_id"] for item in relations}
    assert expansion_ids <= {item["relation_id"] for item in reviewed}
    expansion = [item for item in relations if item["relation_id"] in expansion_ids]
    assert all(item["relation_type"] == "PREREQUISITE" for item in expansion)
    assert all(item["confidence"] == "high" for item in expansion)
    assert all(item["review_status"] == "reviewed_candidate" for item in expansion)
    assert all(item["verification_role"] == "diagnostic_only" for item in expansion)
    held_pairs = {
        ("KN1204", "KN0688"),
        ("KN1053", "KN1311"),
        ("KN0833", "KN1099"),
    }
    assert held_pairs.isdisjoint({
        (item["source_node_id"], item["target_node_id"])
        for item in relations
    })


def test_duplicate_relation_with_a_distinct_id_is_rejected():
    node_ids, question_ids = _formal_ids()
    records = get_node_relations()
    duplicate = copy.deepcopy(records[0])
    duplicate["relation_id"] = "KNR9999"
    records.append(duplicate)
    with pytest.raises(KnowledgeNodeRelationValidationError, match="duplicate relation"):
        validate_node_relations(records, node_ids, question_ids)


def test_merge_candidates_reference_formal_unique_nodes_and_questions():
    node_ids, question_ids = _formal_ids()
    candidates = get_node_merge_candidates()
    validate_merge_candidates(candidates, node_ids, question_ids)
    assert len({item["candidate_id"] for item in candidates}) == len(candidates)
    assert all(len(item["node_ids"]) >= 2 for item in candidates)
    assert all(len(item["node_ids"]) == len(set(item["node_ids"])) for item in candidates)
    assert all(item["review_status"] == "reviewed" for item in candidates)


@pytest.mark.parametrize("mutation", [
    lambda records: records[0].update(candidate_id="bad"),
    lambda records: records[0].update(node_ids=["KN0597", "KN0597"]),
    lambda records: records[0].update(node_ids=["KN9999", "KN0807"]),
    lambda records: records[0].update(question_ids=["Q9999"]),
    lambda records: records[0].update(confidence="certain"),
    lambda records: records[0].update(review_status="automatic"),
    lambda records: records.append(copy.deepcopy(records[0])),
])
def test_invalid_merge_candidate_data_is_rejected(mutation):
    node_ids, question_ids = _formal_ids()
    records = get_node_merge_candidates()
    mutation(records)
    with pytest.raises(KnowledgeNodeRelationValidationError):
        validate_merge_candidates(records, node_ids, question_ids)


def test_existing_question_bank_loader_remains_compatible():
    assert question_count() == 1635
    assert get_question_tag("Q260")["knowledge_node_id"] == "KN0259"
