"""Integrate the validated Question Bank 2000 Batch 01 staging set.

The script is intentionally narrow and idempotent. It allocates Q1738-Q1749,
updates the four formal stores, promotes the 12 target singleton Knowledge Nodes
to confirmed_shared, and advances the bank manifest to Q1749.
"""
from __future__ import annotations

import json
from pathlib import Path

from reports.question_bank_2000_batch01_validate import _accepted_drafts

ROOT = Path(__file__).resolve().parents[1]
BANK = ROOT / "data" / "question_bank"
START_Q = 1738
END_Q = 1749
EXPECTED_BASE_END = 1737
TARGET_VERSION = "2026-09-b13"
LETTERS = "ABCDE"


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


def _map_choice_dict(values: dict[str, str]) -> dict[str, str]:
    ordered = []
    for i, letter in enumerate(LETTERS, start=1):
        value = values.get(str(i), values.get(letter))
        if value is None:
            raise ValueError(f"missing choice {i}/{letter}: {values}")
        ordered.append((letter, value))
    return dict(ordered)


def _map_correct(values: list[str]) -> list[str]:
    result = []
    for value in values:
        value = str(value)
        if value in LETTERS:
            result.append(value)
        elif value.isdigit() and 1 <= int(value) <= 5:
            result.append(LETTERS[int(value) - 1])
        else:
            raise ValueError(f"unsupported correct choice: {value}")
    return result


def integrate() -> None:
    questions_path = BANK / "questions.json"
    answers_path = BANK / "answers.json"
    explanations_path = BANK / "explanations.json"
    tags_path = BANK / "question_tags.json"
    nodes_path = BANK / "knowledge_nodes.json"
    manifest_path = BANK / "bank_manifest.json"

    questions = _read(questions_path)
    answers = _read(answers_path)
    explanations = _read(explanations_path)
    tags = _read(tags_path)
    nodes = _read(nodes_path)
    manifest = _read(manifest_path)

    stores = [questions, answers, explanations, tags]
    indexes = [{row["id"]: row for row in store} for store in stores]
    node_index = {row["knowledge_node_id"]: row for row in nodes}

    drafts = _accepted_drafts()
    if len(drafts) != 12:
        raise ValueError(f"expected 12 accepted drafts, got {len(drafts)}")
    draft_ids = [str(d["draft_id"]) for d in drafts]
    if len(set(draft_ids)) != 12:
        raise ValueError(f"duplicate draft ids: {draft_ids}")
    target_nodes = [str(d["target_node_id"]) for d in drafts]
    if len(set(target_nodes)) != 12 or "KN0779" in target_nodes:
        raise ValueError(f"invalid target nodes: {target_nodes}")

    existing_new = [f"Q{n}" for n in range(START_Q, END_Q + 1) if f"Q{n}" in indexes[0]]
    already_done = len(existing_new) == 12
    if existing_new and not already_done:
        raise ValueError(f"partial Batch01 allocation found: {existing_new}")

    if not already_done:
        if int(manifest["last_question_number"]) != EXPECTED_BASE_END or int(manifest["question_count"]) != EXPECTED_BASE_END:
            raise ValueError(f"unexpected baseline manifest: {manifest}")

        for offset, draft in enumerate(drafts):
            qid = f"Q{START_Q + offset}"
            node_id = str(draft["target_node_id"])
            refs = [str(x) for x in draft.get("reference_question_ids", [])]
            if len(refs) != 1:
                raise ValueError(f"{draft['draft_id']}: expected one singleton reference, got {refs}")
            ref_qid = refs[0]
            node = node_index[node_id]
            if node.get("status") != "singleton_initial" or list(node.get("question_ids", [])) != [ref_qid]:
                raise ValueError(f"{draft['draft_id']}: target is not the expected singleton: {node}")

            category_large = str(draft["proposed_category_large"])
            category_small = int(draft["proposed_category_small"])
            ref_question = indexes[0][ref_qid]
            ref_tag = indexes[3][ref_qid]
            if ref_question["category_large"] != category_large or int(ref_question["category_small"]) != category_small:
                raise ValueError(f"{draft['draft_id']}: category mismatch with {ref_qid}")
            if ref_tag["knowledge_node_id"] != node_id:
                raise ValueError(f"{draft['draft_id']}: node mismatch with {ref_qid}")

            choices = _map_choice_dict(draft["choices"])
            correct = _map_correct(draft["correct_choices"])
            if len(correct) != 1:
                raise ValueError(f"{draft['draft_id']}: Batch01 expects one best answer, got {correct}")

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
    else:
        expected_ids = [f"Q{n}" for n in range(START_Q, END_Q + 1)]
        for index in indexes:
            if not all(qid in index for qid in expected_ids):
                raise ValueError("Batch01 is only partially present across formal stores")
        if int(manifest["last_question_number"]) != END_Q or int(manifest["question_count"]) != END_Q:
            raise ValueError(f"Batch01 records exist but manifest is inconsistent: {manifest}")

    ids = [row["id"] for row in questions]
    if len(ids) != END_Q or ids != [f"Q{n}" for n in range(1, END_Q + 1)]:
        raise ValueError("questions.json must remain a contiguous Q1-Q1749 sequence")
    for store in (answers, explanations, tags):
        if [row["id"] for row in store] != ids:
            raise ValueError("formal store ids/order are inconsistent after integration")

    _write(questions_path, questions)
    _write(answers_path, answers)
    _write(explanations_path, explanations)
    _write(tags_path, tags)
    _write(nodes_path, nodes)
    _write(manifest_path, manifest)


if __name__ == "__main__":
    integrate()
