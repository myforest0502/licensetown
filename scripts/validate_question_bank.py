"""Validate the four formal LicenseTown question-bank JSON files.

The validator is intentionally kept out of the application startup path.  It
uses only the Python standard library so CI and local checks do not require a
new runtime dependency.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BANK_DIR = REPOSITORY_ROOT / "data" / "question_bank"
DEFAULT_SCHEMA_PATH = DEFAULT_BANK_DIR / "schema" / "question_bank_schema_v1.json"
DEFAULT_REGISTRY_PATH = DEFAULT_BANK_DIR / "knowledge_nodes.json"
QUESTION_BANK_FILES = {
    "questions": "questions.json",
    "answers": "answers.json",
    "explanations": "explanations.json",
    "question_tags": "question_tags.json",
}
EXPECTED_QUESTION_COUNT = 1720
EXPECTED_IDS = {f"Q{number}" for number in range(1, EXPECTED_QUESTION_COUNT + 1)}
TASK_PRIMARY_ABILITIES = {
    "fact_recall": "KNOW",
    "finding_interpretation": "INTERPRET",
    "assessment_selection": "MEASURE",
    "intervention_selection": "PRESCRIBE",
    "device_selection": "PRESCRIBE",
    "functional_goal_decision": "DECIDE",
    "prognosis_prediction": "PREDICT",
    "safety_priority": "DECIDE",
}


class QuestionBankValidationError(ValueError):
    """Raised when the formal question bank violates its schema or invariants."""

    def __init__(self, issues: list[str], report: dict[str, Any] | None = None):
        self.issues = tuple(issues)
        self.report = report or {}
        super().__init__("Question bank validation failed:\n- " + "\n- ".join(issues))


def _json_type_matches(value: Any, expected_type: str) -> bool:
    if expected_type == "object":
        return isinstance(value, dict)
    if expected_type == "array":
        return isinstance(value, list)
    if expected_type == "string":
        return isinstance(value, str)
    if expected_type == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected_type == "null":
        return value is None
    raise ValueError(f"Unsupported JSON Schema type: {expected_type}")


def _resolve_ref(root_schema: dict[str, Any], ref: str) -> dict[str, Any]:
    if not ref.startswith("#/"):
        raise ValueError(f"Only local JSON Schema references are supported: {ref}")
    resolved: Any = root_schema
    for component in ref[2:].split("/"):
        component = component.replace("~1", "/").replace("~0", "~")
        resolved = resolved[component]
    if not isinstance(resolved, dict):
        raise ValueError(f"JSON Schema reference does not resolve to an object: {ref}")
    return resolved


def _validate_schema_value(
    value: Any,
    schema: dict[str, Any],
    root_schema: dict[str, Any],
    path: str,
    issues: list[str],
) -> None:
    if "$ref" in schema:
        _validate_schema_value(
            value, _resolve_ref(root_schema, schema["$ref"]), root_schema, path, issues
        )
        return

    if "anyOf" in schema:
        for candidate in schema["anyOf"]:
            candidate_issues: list[str] = []
            _validate_schema_value(value, candidate, root_schema, path, candidate_issues)
            if not candidate_issues:
                break
        else:
            issues.append(f"{path}: does not match any allowed schema")
        return

    expected_types = schema.get("type")
    if expected_types is not None:
        if isinstance(expected_types, str):
            expected_types = [expected_types]
        if not any(_json_type_matches(value, item) for item in expected_types):
            issues.append(f"{path}: expected type {' or '.join(expected_types)}")
            return

    if "enum" in schema and value not in schema["enum"]:
        issues.append(f"{path}: value {value!r} is not in the formal enum")

    if isinstance(value, str):
        if len(value) < schema.get("minLength", 0):
            issues.append(f"{path}: string is shorter than minLength")
        if "pattern" in schema and re.search(schema["pattern"], value) is None:
            issues.append(f"{path}: value {value!r} does not match the required pattern")

    if isinstance(value, int) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            issues.append(f"{path}: value is below minimum {schema['minimum']}")
        if "maximum" in schema and value > schema["maximum"]:
            issues.append(f"{path}: value is above maximum {schema['maximum']}")

    if isinstance(value, list):
        if len(value) < schema.get("minItems", 0):
            issues.append(f"{path}: array has fewer than {schema['minItems']} items")
        if "maxItems" in schema and len(value) > schema["maxItems"]:
            issues.append(f"{path}: array has more than {schema['maxItems']} items")
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for index, item in enumerate(value):
                _validate_schema_value(
                    item, item_schema, root_schema, f"{path}[{index}]", issues
                )

    if isinstance(value, dict):
        if len(value) < schema.get("minProperties", 0):
            issues.append(
                f"{path}: object has fewer than {schema['minProperties']} properties"
            )
        required = schema.get("required", [])
        for key in required:
            if key not in value:
                issues.append(f"{path}: missing required property {key!r}")
        properties = schema.get("properties", {})
        for key, child_schema in properties.items():
            if key in value:
                _validate_schema_value(
                    value[key], child_schema, root_schema, f"{path}.{key}", issues
                )
        additional = schema.get("additionalProperties", True)
        for key in value.keys() - properties.keys():
            if additional is False:
                issues.append(f"{path}: unexpected property {key!r}")
            elif isinstance(additional, dict):
                _validate_schema_value(
                    value[key], additional, root_schema, f"{path}.{key}", issues
                )


def load_question_bank_data(bank_dir: Path = DEFAULT_BANK_DIR) -> dict[str, Any]:
    """Parse all four formal JSON files, reporting parse failures uniformly."""

    loaded: dict[str, Any] = {}
    issues: list[str] = []
    for name, filename in QUESTION_BANK_FILES.items():
        path = bank_dir / filename
        try:
            loaded[name] = json.loads(path.read_text(encoding="utf-8-sig"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            issues.append(f"{filename}: JSON parse failed: {exc}")
    if issues:
        raise QuestionBankValidationError(issues)
    return loaded


def load_schema(schema_path: Path = DEFAULT_SCHEMA_PATH) -> dict[str, Any]:
    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise QuestionBankValidationError(
            [f"{schema_path.name}: JSON parse failed: {exc}"]
        ) from exc
    if not isinstance(schema, dict):
        raise QuestionBankValidationError([f"{schema_path.name}: root must be an object"])
    return schema


def load_registry(registry_path: Path = DEFAULT_REGISTRY_PATH) -> list[dict[str, Any]]:
    try:
        registry = json.loads(registry_path.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise QuestionBankValidationError(
            [f"{registry_path.name}: JSON parse failed: {exc}"]
        ) from exc
    if not isinstance(registry, list):
        raise QuestionBankValidationError(
            [f"{registry_path.name}: root must be an array"]
        )
    return registry


def _records_by_id(records: Any) -> dict[str, dict[str, Any]]:
    if not isinstance(records, list):
        return {}
    return {
        record["id"]: record
        for record in records
        if isinstance(record, dict) and isinstance(record.get("id"), str)
    }


def _validate_registry(
    tags: dict[str, dict[str, Any]],
    registry: Any,
    report: dict[str, Any],
    issues: list[str],
) -> None:
    """Validate stable node IDs and the bidirectional registry mapping."""

    if not isinstance(registry, list):
        issues.append("knowledge_nodes.json: must be a JSON array")
        return

    registry_ids: list[str] = []
    registry_by_id: dict[str, dict[str, Any]] = {}
    question_to_nodes: dict[str, list[str]] = {}
    orphan_nodes = 0
    registry_format_invalid = 0
    confirmed_shared_groups = 0
    confirmed_shared_questions = 0
    singleton_nodes = 0
    required = {
        "knowledge_node_id", "label", "status", "question_ids",
        "aliases", "successor_ids",
    }

    for index, node in enumerate(registry):
        path = f"knowledge_nodes[{index}]"
        if not isinstance(node, dict):
            issues.append(f"{path}: must be an object")
            continue
        missing = required - node.keys()
        if missing:
            issues.append(f"{path}: missing required properties {sorted(missing)}")

        node_id = node.get("knowledge_node_id")
        if not isinstance(node_id, str) or re.fullmatch(r"KN[0-9]{4}", node_id) is None:
            registry_format_invalid += 1
            issues.append(f"{path}: invalid knowledge_node_id {node_id!r}")
            continue
        registry_ids.append(node_id)
        registry_by_id.setdefault(node_id, node)

        if not isinstance(node.get("label"), str) or not node["label"]:
            issues.append(f"{path}: label must be a non-empty string")
        status = node.get("status")
        if status not in {"confirmed_shared", "singleton_initial"}:
            issues.append(f"{path}: invalid status {status!r}")

        question_ids = node.get("question_ids")
        if not isinstance(question_ids, list):
            issues.append(f"{path}: question_ids must be an array")
            question_ids = []
        if not question_ids:
            orphan_nodes += 1
            issues.append(f"{path}: registry node has no question_ids")
        if status == "confirmed_shared":
            confirmed_shared_groups += 1
            confirmed_shared_questions += len(question_ids)
            if len(question_ids) < 2:
                issues.append(f"{path}: confirmed_shared must contain multiple questions")
        elif status == "singleton_initial":
            singleton_nodes += 1
            if len(question_ids) != 1:
                issues.append(f"{path}: singleton_initial must contain exactly one question")

        for q_id in question_ids:
            if not isinstance(q_id, str):
                issues.append(f"{path}: question ID must be a string")
                continue
            question_to_nodes.setdefault(q_id, []).append(node_id)

        for field in ("aliases", "successor_ids"):
            values = node.get(field)
            if not isinstance(values, list) or any(
                not isinstance(value, str) for value in values
            ):
                issues.append(f"{path}: {field} must be an array of strings")

    registry_id_duplicates = sum(
        count - 1 for count in Counter(registry_ids).values() if count > 1
    )
    if registry_id_duplicates:
        issues.append(
            f"knowledge_nodes.json: contains {registry_id_duplicates} duplicate node IDs"
        )

    multiply_assigned_questions = sum(
        1 for node_ids in question_to_nodes.values() if len(node_ids) > 1
    )
    if multiply_assigned_questions:
        issues.append(
            f"knowledge_nodes.json: {multiply_assigned_questions} questions map to multiple nodes"
        )
    missing_registry_questions = EXPECTED_IDS - question_to_nodes.keys()
    unexpected_registry_questions = question_to_nodes.keys() - EXPECTED_IDS
    if missing_registry_questions:
        issues.append(
            f"knowledge_nodes.json: missing {len(missing_registry_questions)} question IDs"
        )
    if unexpected_registry_questions:
        issues.append(
            "knowledge_nodes.json: contains "
            f"{len(unexpected_registry_questions)} unexpected question IDs"
        )

    present_node_ids = 0
    empty_node_ids = 0
    tag_format_invalid = 0
    tag_nodes_missing_from_registry = 0
    mapping_mismatches = 0
    tag_node_ids: set[str] = set()
    for q_id, tag in tags.items():
        node_id = tag.get("knowledge_node_id")
        if isinstance(node_id, str) and node_id:
            present_node_ids += 1
            tag_node_ids.add(node_id)
        else:
            empty_node_ids += 1
            continue
        if re.fullmatch(r"KN[0-9]{4}", node_id) is None:
            tag_format_invalid += 1
        if node_id not in registry_by_id:
            tag_nodes_missing_from_registry += 1
        if question_to_nodes.get(q_id) != [node_id]:
            mapping_mismatches += 1

    unreferenced_registry_nodes = len(set(registry_ids) - tag_node_ids)
    if empty_node_ids:
        issues.append(f"question_tags: {empty_node_ids} knowledge_node_id values are empty")
    if tag_format_invalid:
        issues.append(
            f"question_tags: {tag_format_invalid} knowledge_node_id values have invalid format"
        )
    if tag_nodes_missing_from_registry:
        issues.append(
            "question_tags: "
            f"{tag_nodes_missing_from_registry} node IDs do not exist in the registry"
        )
    if mapping_mismatches:
        issues.append(
            f"question_tags/registry: {mapping_mismatches} bidirectional mappings differ"
        )
    if unreferenced_registry_nodes:
        issues.append(
            f"knowledge_nodes.json: {unreferenced_registry_nodes} nodes are not used by tags"
        )

    report.update({
        "knowledge_node_id_present": present_node_ids,
        "knowledge_node_id_empty": empty_node_ids,
        "knowledge_node_id_format_invalid": tag_format_invalid,
        "registry_node_count": len(registry),
        "registry_id_duplicate": registry_id_duplicates,
        "registry_id_format_invalid": registry_format_invalid,
        "registry_missing_question": len(missing_registry_questions),
        "registry_unexpected_question": len(unexpected_registry_questions),
        "registry_multiple_node_question": multiply_assigned_questions,
        "registry_orphan_node": orphan_nodes,
        "registry_unreferenced_node": unreferenced_registry_nodes,
        "registry_mapping_mismatch": mapping_mismatches,
        "registry_confirmed_shared_groups": confirmed_shared_groups,
        "registry_confirmed_shared_questions": confirmed_shared_questions,
        "registry_singleton_nodes": singleton_nodes,
    })


def validate_question_bank_data(
    data: dict[str, Any],
    schema: dict[str, Any],
    registry: Any | None = None,
) -> dict[str, Any]:
    """Validate the formal schema plus all cross-file and tag invariants."""

    issues: list[str] = []
    _validate_schema_value(data, schema, schema, "$", issues)

    report: dict[str, Any] = {"counts": {}, "missing": {}, "duplicates": {}}
    id_sets: dict[str, set[str]] = {}
    for name in QUESTION_BANK_FILES:
        records = data.get(name)
        if not isinstance(records, list):
            report["counts"][name] = 0
            report["missing"][name] = EXPECTED_QUESTION_COUNT
            report["duplicates"][name] = 0
            issues.append(f"{name}: must be a JSON array")
            id_sets[name] = set()
            continue

        ids = [
            record.get("id")
            for record in records
            if isinstance(record, dict) and isinstance(record.get("id"), str)
        ]
        id_counts = Counter(ids)
        duplicates = sum(count - 1 for count in id_counts.values() if count > 1)
        missing = EXPECTED_IDS - set(ids)
        unexpected = set(ids) - EXPECTED_IDS
        report["counts"][name] = len(records)
        report["missing"][name] = len(missing)
        report["duplicates"][name] = duplicates
        id_sets[name] = set(ids)
        if len(records) != EXPECTED_QUESTION_COUNT:
            issues.append(
                f"{name}: expected {EXPECTED_QUESTION_COUNT} records, found {len(records)}"
            )
        if missing:
            issues.append(f"{name}: missing {len(missing)} formal IDs")
        if duplicates:
            issues.append(f"{name}: contains {duplicates} duplicate IDs")
        if unexpected:
            issues.append(f"{name}: contains {len(unexpected)} unexpected IDs")

    all_ids = set().union(*id_sets.values())
    common_ids = set.intersection(*id_sets.values()) if id_sets else set()
    report["id_mismatch"] = len(all_ids - common_ids)
    if report["id_mismatch"]:
        issues.append(
            f"cross-file IDs: {report['id_mismatch']} IDs are not present in all files"
        )

    questions = _records_by_id(data.get("questions"))
    answers = _records_by_id(data.get("answers"))
    explanations = _records_by_id(data.get("explanations"))
    tags = _records_by_id(data.get("question_tags"))

    choice_key_mismatches = 0
    for q_id in questions.keys() & explanations.keys():
        choice_keys = set(questions[q_id].get("choices", {}))
        explanation_keys = set(explanations[q_id].get("choice_explanations", {}))
        if choice_keys != explanation_keys:
            choice_key_mismatches += 1
            issues.append(f"{q_id}: choices and choice_explanations keys differ")
    report["choice_key_mismatch"] = choice_key_mismatches

    invalid_accepted_answers = 0
    for q_id in questions.keys() & answers.keys():
        choice_keys = set(questions[q_id].get("choices", {}))
        accepted_sets = answers[q_id].get("accepted_answer_sets", [])
        if not isinstance(accepted_sets, list):
            continue
        for accepted_set in accepted_sets:
            if not isinstance(accepted_set, list):
                continue
            for answer_key in accepted_set:
                if answer_key not in choice_keys:
                    invalid_accepted_answers += 1
                    issues.append(
                        f"{q_id}: accepted answer {answer_key!r} is not a choice key"
                    )
    report["invalid_accepted_answer"] = invalid_accepted_answers

    task_primary_mismatches = 0
    secondary_self_duplicates = 0
    safety_contradictions = 0
    forbidden_nodes = 0
    for q_id, tag in tags.items():
        expected_primary = TASK_PRIMARY_ABILITIES.get(tag.get("task"))
        if expected_primary is not None and tag.get("primary_ability") != expected_primary:
            task_primary_mismatches += 1
            issues.append(f"{q_id}: task and primary_ability do not match")
        secondary = tag.get("secondary_ability")
        if secondary is not None and secondary == tag.get("primary_ability"):
            secondary_self_duplicates += 1
            issues.append(f"{q_id}: secondary_ability duplicates primary_ability")
        if tag.get("task") == "safety_priority" and tag.get("safety") == "none":
            safety_contradictions += 1
            issues.append(f"{q_id}: safety_priority cannot have safety=none")
        if tag.get("knowledge_node") == "cause_identification":
            forbidden_nodes += 1
            issues.append(f"{q_id}: cause_identification is forbidden")

    report["task_primary_mismatch"] = task_primary_mismatches
    report["secondary_self_duplicate"] = secondary_self_duplicates
    report["safety_contradiction"] = safety_contradictions
    report["cause_identification"] = forbidden_nodes
    if registry is not None:
        _validate_registry(tags, registry, report, issues)
    report["schema_issue_count"] = len(issues)

    if issues:
        raise QuestionBankValidationError(issues, report)
    return report


def validate_question_bank(
    bank_dir: Path = DEFAULT_BANK_DIR,
    schema_path: Path = DEFAULT_SCHEMA_PATH,
    registry_path: Path | None = None,
) -> dict[str, Any]:
    """Load and validate the repository's formal question bank."""

    selected_registry_path = registry_path or bank_dir / DEFAULT_REGISTRY_PATH.name
    return validate_question_bank_data(
        load_question_bank_data(bank_dir),
        load_schema(schema_path),
        load_registry(selected_registry_path),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bank-dir", type=Path, default=DEFAULT_BANK_DIR)
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA_PATH)
    parser.add_argument("--registry", type=Path, default=None)
    args = parser.parse_args()
    try:
        report = validate_question_bank(args.bank_dir, args.schema, args.registry)
    except QuestionBankValidationError as exc:
        print(str(exc))
        return 1
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
