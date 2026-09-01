import copy

import pytest

from scripts.validate_question_bank import (
    DEFAULT_REGISTRY_PATH,
    DEFAULT_SCHEMA_PATH,
    QuestionBankValidationError,
    load_question_bank_data,
    load_registry,
    load_schema,
    validate_question_bank,
    validate_question_bank_data,
)


def test_formal_schema_is_v1_and_covers_all_four_json_files():
    schema = load_schema(DEFAULT_SCHEMA_PATH)

    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert schema["title"] == "LicenseTown Question Bank Schemas v1.0"
    assert set(schema["properties"]) == {
        "questions", "answers", "explanations", "question_tags",
    }
    # The formal data uses null for the 500 original questions and an object
    # for the 1064 past-exam questions, as allowed by the written v1.0 spec.
    assert schema["properties"]["questions"]["items"]["properties"]["exam"][
        "type"
    ] == ["object", "null"]
    tag_schema = schema["properties"]["question_tags"]["items"]
    assert "knowledge_node_id" in tag_schema["required"]
    assert tag_schema["properties"]["knowledge_node_id"] == {
        "type": "string",
        "pattern": "^KN[0-9]{4}$",
    }


def test_formal_question_bank_passes_schema_and_cross_file_validation():
    report = validate_question_bank()

    assert report["counts"] == {
        "questions": 1605,
        "answers": 1605,
        "explanations": 1605,
        "question_tags": 1605,
    }
    assert report["missing"] == {
        "questions": 0,
        "answers": 0,
        "explanations": 0,
        "question_tags": 0,
    }
    assert report["duplicates"] == {
        "questions": 0,
        "answers": 0,
        "explanations": 0,
        "question_tags": 0,
    }
    assert report["id_mismatch"] == 0
    assert report["choice_key_mismatch"] == 0
    assert report["invalid_accepted_answer"] == 0
    assert report["task_primary_mismatch"] == 0
    assert report["secondary_self_duplicate"] == 0
    assert report["safety_contradiction"] == 0
    assert report["cause_identification"] == 0
    assert report["knowledge_node_id_present"] == 1605
    assert report["knowledge_node_id_empty"] == 0
    assert report["knowledge_node_id_format_invalid"] == 0
    assert report["registry_node_count"] == 1538
    assert report["registry_confirmed_shared_groups"] == 66
    assert report["registry_confirmed_shared_questions"] == 133
    assert report["registry_singleton_nodes"] == 1472
    assert report["registry_id_duplicate"] == 0
    assert report["registry_id_format_invalid"] == 0
    assert report["registry_missing_question"] == 0
    assert report["registry_unexpected_question"] == 0
    assert report["registry_multiple_node_question"] == 0
    assert report["registry_orphan_node"] == 0
    assert report["registry_unreferenced_node"] == 0
    assert report["registry_mapping_mismatch"] == 0
    assert report["schema_issue_count"] == 0


def test_registry_allows_confirmed_shared_ids_and_maps_every_question_once():
    registry = load_registry(DEFAULT_REGISTRY_PATH)
    shared = [node for node in registry if node["status"] == "confirmed_shared"]
    mapped_questions = [q_id for node in registry for q_id in node["question_ids"]]

    assert len(shared) == 66
    assert sum(len(node["question_ids"]) for node in shared) == 133
    assert all(len(node["question_ids"]) >= 2 for node in shared)
    assert len(mapped_questions) == len(set(mapped_questions)) == 1605


def test_validator_detects_cross_file_answer_and_tag_contradictions():
    data = copy.deepcopy(load_question_bank_data())
    schema = load_schema()
    data["explanations"][0]["choice_explanations"].pop(
        next(iter(data["explanations"][0]["choice_explanations"]))
    )
    data["answers"][0]["accepted_answer_sets"][0].append("not-a-choice")
    data["question_tags"][0]["primary_ability"] = "DECIDE"
    data["question_tags"][1]["secondary_ability"] = data["question_tags"][1][
        "primary_ability"
    ]
    data["question_tags"][2]["task"] = "safety_priority"
    data["question_tags"][2]["primary_ability"] = "DECIDE"
    data["question_tags"][2]["safety"] = "none"
    data["question_tags"][3]["knowledge_node"] = "cause_identification"

    with pytest.raises(QuestionBankValidationError) as captured:
        validate_question_bank_data(data, schema)

    report = captured.value.report
    assert report["choice_key_mismatch"] == 1
    assert report["invalid_accepted_answer"] == 1
    assert report["task_primary_mismatch"] >= 1
    assert report["secondary_self_duplicate"] == 1
    assert report["safety_contradiction"] == 1
    assert report["cause_identification"] == 1


def test_validator_detects_missing_and_duplicate_ids():
    data = copy.deepcopy(load_question_bank_data())
    schema = load_schema()
    data["questions"][0]["id"] = data["questions"][1]["id"]

    with pytest.raises(QuestionBankValidationError) as captured:
        validate_question_bank_data(data, schema)

    assert captured.value.report["missing"]["questions"] == 1
    assert captured.value.report["duplicates"]["questions"] == 1
    assert captured.value.report["id_mismatch"] == 1


def test_validator_detects_registry_mapping_duplicate_and_orphan_nodes():
    data = copy.deepcopy(load_question_bank_data())
    schema = load_schema()
    registry = copy.deepcopy(load_registry())
    registry[0]["question_ids"].append(registry[1]["question_ids"][0])
    registry.append({
        "knowledge_node_id": registry[0]["knowledge_node_id"],
        "label": "duplicate and orphan",
        "status": "singleton_initial",
        "question_ids": [],
        "aliases": [],
        "successor_ids": [],
    })

    with pytest.raises(QuestionBankValidationError) as captured:
        validate_question_bank_data(data, schema, registry)

    report = captured.value.report
    assert report["registry_id_duplicate"] == 1
    assert report["registry_multiple_node_question"] == 1
    assert report["registry_orphan_node"] == 1
    assert report["registry_mapping_mismatch"] >= 1
