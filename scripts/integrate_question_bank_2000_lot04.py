"""Atomically integrate sealed Question Bank 2000 Lot04 as Q1906-Q1953.

All inputs are validated in memory before any formal file is written. Passing a
temporary bank directory provides a dry-run; rerunning a completed integration is
idempotent and rejects partial allocation.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from reports.question_bank_2000_lot04_validate import (
    STAGING, build_report, draft_fingerprint, file_fingerprint,
)
from reports.question_bank_2000_lot02_validate import read
from knowledge_node_canonical import canonicalize_knowledge_node_id

BANK = ROOT / "data" / "question_bank"
START_Q = 1906
END_Q = 1953
EXPECTED_BASE_END = 1905
TARGET_VERSION = "2026-09-b18"
START_NODE = 1552
END_NODE = 1555
LETTERS = "ABCDE"
QID_PATTERN = r"^Q(?:[1-9]|[1-9][0-9]{1,2}|1[0-8][0-9]{2}|19[0-4][0-9]|195[0-3])$"
IMMUTABLE_FILES = ("knowledge_node_canonical_map.json", "strong_different_question_pairs.json")


def _write(path: Path, payload) -> None:
    raw = path.read_bytes()
    data = (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    path.write_bytes((b"\xef\xbb\xbf" if raw.startswith(b"\xef\xbb\xbf") else b"") + data)


def _accepted_drafts(staging_path: Path) -> list[dict]:
    payload = read(staging_path)
    drafts = [row for row in payload.get("drafts", []) if row.get("status") == "accepted"]
    if len(drafts) != 48:
        raise ValueError(f"expected 48 accepted drafts, got {len(drafts)}")
    if len({row.get("draft_id") for row in drafts}) != 48:
        raise ValueError("duplicate draft ids")
    for draft in drafts:
        if draft.get("reviewed_sha256") != draft_fingerprint(draft):
            raise ValueError(f"{draft.get('draft_id')}: staging content changed after review")
    return drafts


def _choice_map(values: dict[str, str]) -> dict[str, str]:
    result = {}
    for number, letter in enumerate(LETTERS, 1):
        value = values.get(str(number), values.get(letter))
        if value is None:
            raise ValueError(f"missing choice {number}/{letter}")
        result[letter] = str(value)
    return result


def _correct_letters(values: list[str]) -> list[str]:
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


def _set_schema_contract(schema: dict) -> None:
    schema["$defs"]["qid"]["pattern"] = QID_PATTERN
    for name in ("questions", "answers", "explanations", "question_tags"):
        schema["properties"][name]["minItems"] = END_Q
        schema["properties"][name]["maxItems"] = END_Q


def _category_large(questions: list[dict], category_small: int) -> str:
    values = {str(row.get("category_large")) for row in questions if int(row.get("category_small")) == category_small}
    if len(values) != 1:
        raise ValueError(f"ambiguous category_large for category {category_small}: {values}")
    return values.pop()


def integrate(bank_dir: Path = BANK, staging_path: Path = STAGING) -> None:
    paths = {
        "questions": bank_dir / "questions.json",
        "answers": bank_dir / "answers.json",
        "explanations": bank_dir / "explanations.json",
        "question_tags": bank_dir / "question_tags.json",
        "nodes": bank_dir / "knowledge_nodes.json",
        "manifest": bank_dir / "bank_manifest.json",
        "schema": bank_dir / "schema/question_bank_schema_v1.json",
    }
    questions = read(paths["questions"])
    answers = read(paths["answers"])
    explanations = read(paths["explanations"])
    tags = read(paths["question_tags"])
    nodes = read(paths["nodes"])
    manifest = read(paths["manifest"])
    schema = read(paths["schema"])
    drafts = _accepted_drafts(staging_path)
    stores = (questions, answers, explanations, tags)
    indexes = [{row["id"]: row for row in store} for store in stores]
    node_index = {row["knowledge_node_id"]: row for row in nodes}
    target_ids = [f"Q{number}" for number in range(START_Q, END_Q + 1)]
    present = [qid for qid in target_ids if qid in indexes[0]]
    integrated = len(present) == len(target_ids)
    if present and not integrated:
        raise ValueError(f"partial Lot04 allocation found: {present}")

    new_drafts = [row for row in drafts if row.get("slot_type") == "new_node"]
    if len(new_drafts) != END_NODE - START_NODE + 1:
        raise ValueError(f"expected four new Node drafts, got {len(new_drafts)}")
    new_node_by_draft = {row["draft_id"]: f"KN{START_NODE + offset:04d}" for offset, row in enumerate(new_drafts)}

    if not integrated:
        payload = read(staging_path)
        report = build_report(payload)
        if report["hard_errors"] or report["warnings"]:
            raise ValueError(f"Lot04 staging validator failed: {report}")
        if manifest.get("question_count") != EXPECTED_BASE_END or manifest.get("last_question_number") != EXPECTED_BASE_END:
            raise ValueError(f"unexpected baseline manifest: {manifest}")
        for name in IMMUTABLE_FILES:
            expected = payload.get("formal_input_sha256", {}).get(name)
            if expected != file_fingerprint(bank_dir / name):
                raise ValueError(f"immutable formal input changed: {name}")
        counts = schema["properties"]["questions"]
        if (counts.get("minItems"), counts.get("maxItems")) != (EXPECTED_BASE_END, EXPECTED_BASE_END):
            raise ValueError("unexpected baseline schema count")
        existing_numbers = {int(node_id[2:]) for node_id in node_index}
        if any(number in existing_numbers for number in range(START_NODE, END_NODE + 1)):
            raise ValueError("new Knowledge Node ID collision")

        categories = sorted({int(draft["proposed_category_small"]) for draft in drafts})
        category_large = {small: _category_large(questions, small) for small in categories}
        for offset, draft in enumerate(drafts):
            qid = target_ids[offset]
            is_new = draft.get("slot_type") == "new_node"
            node_id = new_node_by_draft.get(draft["draft_id"], str(draft.get("target_node_id") or ""))
            refs = [str(value) for value in draft.get("reference_question_ids", [])]
            if is_new:
                if refs or draft.get("target_node_id") is not None:
                    raise ValueError(f"{draft['draft_id']}: invalid new Node staging contract")
                node = {
                    "knowledge_node_id": node_id,
                    "label": str(draft["target_node_label"]),
                    "status": "singleton_initial",
                    "question_ids": [qid],
                    "aliases": [],
                    "successor_ids": [],
                }
                nodes.append(node)
                node_index[node_id] = node
                prerequisites = []
                large = category_large[int(draft["proposed_category_small"])]
            else:
                node = node_index.get(node_id)
                if node is None or not refs:
                    raise ValueError(f"{draft['draft_id']}: target Node/reference missing")
                if not all(ref in indexes[0] and ref in indexes[3] for ref in refs):
                    raise ValueError(f"{draft['draft_id']}: reference missing")
                own_refs = [ref for ref in refs if indexes[3][ref].get("knowledge_node_id") == node_id]
                if list(node.get("question_ids", [])) != own_refs:
                    raise ValueError(f"{draft['draft_id']}: target membership changed")
                reference_tags = [indexes[3][ref] for ref in refs]
                if any(canonicalize_knowledge_node_id(tag.get("knowledge_node_id")) != node_id for tag in reference_tags):
                    raise ValueError(f"{draft['draft_id']}: reference Node mismatch")
                prior_demands = {(tag.get("task"), tag.get("primary_ability")) for tag in reference_tags}
                demand = (draft.get("proposed_task"), draft.get("primary_ability"))
                if demand in prior_demands:
                    raise ValueError(f"{draft['draft_id']}: no different metadata demand")
                large_values = {str(indexes[0][ref]["category_large"]) for ref in refs}
                small_values = {int(indexes[0][ref]["category_small"]) for ref in refs}
                if len(large_values) != 1 or small_values != {int(draft["proposed_category_small"])}:
                    raise ValueError(f"{draft['draft_id']}: category mismatch")
                large = large_values.pop()
                prerequisites = list(reference_tags[0].get("prerequisite_nodes", []))
                node["question_ids"].append(qid)
                node["status"] = "confirmed_shared"

            choices = _choice_map(draft["choices"])
            correct = _correct_letters(draft["correct_choices"])
            if len(correct) != 1:
                raise ValueError(f"{draft['draft_id']}: single best answer required")
            small = int(draft["proposed_category_small"])
            questions.append({
                "id": qid, "management_code": f"{qid}-{large}-{small}-O",
                "category_large": large, "category_small": small, "source": "O",
                "title": draft.get("title"), "question_text": draft["question_text"],
                "choices": choices, "exam": None,
            })
            answers.append({"id": qid, "display_answer": correct[0], "accepted_answer_sets": [correct], "answer_basis": "LT_original"})
            explanations.append({"id": qid, "explanation": draft["explanation"], "choice_explanations": _choice_map(draft["choice_explanations"])})
            tags.append({
                "id": qid, "theme": draft.get("title"), "knowledge_node": node["label"],
                "knowledge_node_id": node_id, "task": draft["proposed_task"],
                "primary_ability": draft["primary_ability"], "secondary_ability": draft.get("secondary_ability"),
                "level": int(draft["level"]), "safety": draft["safety"],
                "prerequisite_nodes": prerequisites, "tag_version": "1.0",
                "tag_status": "reviewed", "source": "original",
            })

        manifest["bank_version"] = TARGET_VERSION
        manifest["last_question_number"] = END_Q
        manifest["question_count"] = END_Q
        _set_schema_contract(schema)
    else:
        if any(not all(qid in index for index in indexes) for qid in target_ids):
            raise ValueError("Lot04 is partially present across formal stores")
        if (manifest.get("question_count"), manifest.get("last_question_number"), manifest.get("bank_version")) != (END_Q, END_Q, TARGET_VERSION):
            raise ValueError("integrated manifest contract mismatch")

    expected_ids = [f"Q{number}" for number in range(1, END_Q + 1)]
    if any([row["id"] for row in store] != expected_ids for store in stores):
        raise ValueError("formal stores are not a contiguous aligned Q1-Q1953 sequence")
    if len(node_index) != len(nodes) or len(nodes) != len({row["knowledge_node_id"] for row in nodes}):
        raise ValueError("Knowledge Node registry contains duplicate IDs")
    if not all(re.fullmatch(QID_PATTERN, qid) for qid in expected_ids):
        raise ValueError("schema QID pattern mismatch")

    for path, payload in (
        (paths["questions"], questions), (paths["answers"], answers),
        (paths["explanations"], explanations), (paths["question_tags"], tags),
        (paths["nodes"], nodes), (paths["manifest"], manifest), (paths["schema"], schema),
    ):
        _write(path, payload)


if __name__ == "__main__":
    integrate()
