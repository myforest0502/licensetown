import copy

import pytest

from scripts.validate_question_bank import (
    DEFAULT_SCHEMA_PATH,
    QuestionBankValidationError,
    load_question_bank_data,
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


def test_formal_question_bank_passes_schema_and_cross_file_validation():
    report = validate_question_bank()

    assert report["counts"] == {
        "questions": 1564,
        "answers": 1564,
        "explanations": 1564,
        "question_tags": 1564,
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
    assert report["schema_issue_count"] == 0


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
