"""Integrate the validated Question Bank 2000 Batch 02 staging set.

The script is intentionally narrow and idempotent. It allocates Q1750-Q1761,
updates the four formal stores, promotes the 12 target singleton Knowledge Nodes
to confirmed_shared, and advances the manifest/schema contract to Q1761.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from reports.question_bank_2000_batch02_validate import STAGING, build_report, draft_fingerprint

BANK = ROOT / "data" / "question_bank"
START_Q = 1750
END_Q = 1761
EXPECTED_BASE_END = 1749
TARGET_VERSION = "2026-09-b14"
LETTERS = "ABCDE"
QID_PATTERN = r"^Q(?:[1-9]|[1-9][0-9]{1,2}|1[0-6][0-9]{2}|17(?:[0-5][0-9]|6[01]))$"


def _read(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _write(path: Path, payload) -> None:
    raw = path.read_bytes()
    has_bom = raw.startswith(b"\xef\xbb\xbf")
    text = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    data = text.encode("utf-8")
    if has_bom:
        data = b"\xef\xbb\xbf" + data
    path.write_bytes(data)


def _accepted_drafts(staging_path: Path = STAGING) -> list[dict]:
    payload = _read(staging_path)
    drafts = [draft for draft in payload.get("drafts", []) if draft.get("status") == "accepted"]
    if len(drafts) != 12:
        raise ValueError(f"expected 12 accepted drafts, got {len(drafts)}")
    ids = [str(draft.get("draft_id")) for draft in drafts]
    if len(set(ids)) != 12:
        raise ValueError(f"duplicate draft ids: {ids}")
    for draft in drafts:
        if draft.get("reviewed_sha256") != draft_fingerprint(draft):
            raise ValueError(f"{draft.get('draft_id')}: staging content changed after review")
    return drafts


def _map_choice_dict(values: dict[str, str]) -> dict[str, str]:
    ordered = []
    for index, letter in enumerate(LETTERS, start=1):
        value = values.get(str(index), values.get(letter))
        if value is None:
            raise ValueError(f"missing choice {index}/{letter}: {values}")
        ordered.append((letter, str(value)))
    return dict(ordered)


def _map_correct(values: list[str]) -> list[str]:
    result = []
    for value in values:
        text = str(value)
        if text in LETTERS:
            result.append(text)
        elif text.isdigit() and 1 <= int(text) <= 5:
            result.append(LETTERS[int(text) - 1])
        else:
            raise ValueError(f"unsupported correct choice: {value}")
    return result


def _schema_contract(schema: dict) -> tuple[int, int, str]:
    questions = schema["properties"]["questions"]
    return int(questions.get("minItems", 0)), int(questions.get("maxItems", 0)), str(schema["$defs"]["qid"]["pattern"])


def _set_schema_contract(schema: dict) -> None:
    schema["$defs"]["qid"]["pattern"] = QID_PATTERN
    for name in ("questions", "answers", "explanations", "question_tags"):
        schema["properties"][name]["minItems"] = END_Q
        schema["properties"][name]["maxItems"] = END_Q


def integrate(bank_dir: Path = BANK, staging_path: Path = STAGING) -> None:
    questions_path = bank_dir / "questions.json"
    answers_path = bank_dir / "answers.json"
    explanations_path = bank_dir / "explanations.json"
    tags_path = bank_dir / "question_tags.json"
    nodes_path = bank_dir / "knowledge_nodes.json"
    manifest_path = bank_dir / "bank_manifest.json"
    schema_path = bank_dir / "schema/question_bank_schema_v1.json"

    questions = _read(questions_path)
    answers = _read(answers_path)
    explanations = _read(explanations_path)
    tags = _read(tags_path)
    nodes = _read(nodes_path)
    manifest = _read(manifest_path)
    schema = _read(schema_path)

    stores = [questions, answers, explanations, tags]
    indexes = [{row["id"]: row for row in store} for store in stores]
    node_index = {row["knowledge_node_id"]: row for row in nodes}
    drafts = _accepted_drafts(staging_path)

    target_nodes = [str(draft["target_node_id"]) for draft in drafts]
    if len(set(target_nodes)) != 12 or "KN0779" in target_nodes:
        raise ValueError(f"invalid target nodes: {target_nodes}")

    expected_new_ids = [f"Q{number}" for number in range(START_Q, END_Q + 1)]
    existing_new = [qid for qid in expected_new_ids if qid in indexes[0]]
    already_done = len(existing_new) == len(expected_new_ids)
    if existing_new and not already_done:
        raise ValueError(f"partial Batch02 allocation found: {existing_new}")

    if not already_done:
        payload = _read(staging_path)
        report = build_report(payload, bank_dir)
        if report["hard_errors"]:
            raise ValueError(f"Batch02 staging validator failed: {report['hard_errors']}")
        if int(report["formal_count"]) != EXPECTED_BASE_END:
            raise ValueError(f"unexpected staging formal count: {report['formal_count']}")
        if int(manifest["last_question_number"]) != EXPECTED_BASE_END or int(manifest["question_count"]) != EXPECTED_BASE_END:
            raise ValueError(f"unexpected baseline manifest: {manifest}")

        schema_min, schema_max, _ = _schema_contract(schema)
        if (schema_min, schema_max) != (EXPECTED_BASE_END, EXPECTED_BASE_END):
            raise ValueError(f"unexpected baseline schema count: {(schema_min, schema_max)}")

        for offset, draft in enumerate(drafts):
            qid = f"Q{START_Q + offset}"
            node_id = str(draft["target_node_id"])
            refs = [str(value) for value in draft.get("reference_question_ids", [])]
            if len(refs) != 1:
                raise ValueError(f"{draft['draft_id']}: expected one singleton reference, got {refs}")
            ref_qid = refs[0]
            node = node_index.get(node_id)
            if node is None:
                raise ValueError(f"{draft['draft_id']}: missing target node {node_id}")
            if node.get("status") != "singleton_initial" or list(node.get("question_ids", [])) != [ref_qid]:
                raise ValueError(f"{draft['draft_id']}: target is not the expected singleton: {node}")

            ref_question = indexes[0][ref_qid]
            ref_tag = indexes[3][ref_qid]
            category_large = str(draft["proposed_category_large"])
            category_small = int(draft["proposed_category_small"])
            if ref_question["category_large"] != category_large or int(ref_question["category_small"]) != category_small:
                raise ValueError(f"{draft['draft_id']}: category mismatch with {ref_qid}")
            if ref_tag["knowledge_node_id"] != node_id:
                raise ValueError(f"{draft['draft_id']}: node mismatch with {ref_qid}")
            if (ref_tag.get("task"), ref_tag.get("primary_ability")) == (draft.get("proposed_task"), draft.get("primary_ability")):
                raise ValueError(f"{draft['draft_id']}: candidate does not create a different metadata demand")

            choices = _map_choice_dict(draft["choices"])
            correct = _map_correct(draft["correct_choices"])
            if len(correct) != 1:
                raise ValueError(f"{draft['draft_id']}: expected one best answer, got {correct}")

            questions.append({
                "id": qid,
                "management_code": f"{qid}-{category_large}-{category_small}-O",
                "category_large": category_large,
                "category_small": category_small,
                "source": "O",
                "title": draft.get("title"),
                "question_text": draft["question_text"],
                "choices": choices,
                "exam": None,
            })
            answers.append({
                "id": qid,
                "display_answer": correct[0],
                "accepted_answer_sets": [correct],
                "answer_basis": "LT_original",
            })
            explanations.append({
                "id": qid,
                "explanation": draft["explanation"],
                "choice_explanations": _map_choice_dict(draft["choice_explanations"]),
            })
            tags.append({
                "id": qid,
                "theme": draft.get("title"),
                "knowledge_node": node["label"],
                "knowledge_node_id": node_id,
                "task": draft["proposed_task"],
                "primary_ability": draft["primary_ability"],
                "secondary_ability": draft.get("secondary_ability"),
                "level": int(draft["level"]),
                "safety": draft["safety"],
                "prerequisite_nodes": list(ref_tag.get("prerequisite_nodes", [])),
                "tag_version": "1.0",
                "tag_status": "reviewed",
                "source": "original",
            })
            node["question_ids"].append(qid)
            node["status"] = "confirmed_shared"

        manifest["bank_version"] = TARGET_VERSION
        manifest["last_question_number"] = END_Q
        manifest["question_count"] = END_Q
        _set_schema_contract(schema)
    else:
        for index in indexes:
            if not all(qid in index for qid in expected_new_ids):
                raise ValueError("Batch02 is only partially present across formal stores")
        if int(manifest["last_question_number"]) != END_Q or int(manifest["question_count"]) != END_Q:
            raise ValueError(f"Batch02 records exist but manifest is inconsistent: {manifest}")
        schema_min, schema_max, schema_pattern = _schema_contract(schema)
        if (schema_min, schema_max, schema_pattern) != (END_Q, END_Q, QID_PATTERN):
            raise ValueError("Batch02 records exist but schema contract is inconsistent")

    ids = [row["id"] for row in questions]
    expected_ids = [f"Q{number}" for number in range(1, END_Q + 1)]
    if len(ids) != END_Q or ids != expected_ids:
        raise ValueError("questions.json must remain a contiguous Q1-Q1761 sequence")
    for store in (answers, explanations, tags):
        if [row["id"] for row in store] != ids:
            raise ValueError("formal store ids/order are inconsistent after integration")

    for offset, draft in enumerate(drafts):
        qid = f"Q{START_Q + offset}"
        node = node_index[str(draft["target_node_id"])]
        ref_qid = str(draft["reference_question_ids"][0])
        if list(node.get("question_ids", [])) != [ref_qid, qid] or node.get("status") != "confirmed_shared":
            raise ValueError(f"{draft['draft_id']}: integrated Node transition is inconsistent")
        if not re.fullmatch(QID_PATTERN, qid):
            raise ValueError(f"{draft['draft_id']}: integrated Q ID violates schema pattern")

    _write(questions_path, questions)
    _write(answers_path, answers)
    _write(explanations_path, explanations)
    _write(tags_path, tags)
    _write(nodes_path, nodes)
    _write(manifest_path, manifest)
    _write(schema_path, schema)


if __name__ == "__main__":
    integrate()
