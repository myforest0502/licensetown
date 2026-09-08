"""Read-only validation for Question Bank 2000 Batch 01 staging drafts.

This module never imports app/database, never writes Question Bank data, and never
allocates Q IDs.  It compares staging drafts with the current four formal stores
and Knowledge Node registry so category/reference/duplicate checks are
reproducible before any integration branch is created.
"""
from __future__ import annotations

import json
import re
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BANK_DIR = ROOT / "data" / "question_bank"
STAGING_DIR = ROOT / "staging"
MAIN_DRAFT_PATH = STAGING_DIR / "question_bank_2000_batch01_v01.json"
REPLACEMENT_PATH = STAGING_DIR / "question_bank_2000_batch01_replacement_v01.json"

HOLD_IDS = {"B01-05"}
REPLACEMENT_ID = "B01-R1"


def _read(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _index(records: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {str(record["id"]): record for record in records}


def _normalize(text: str) -> str:
    return re.sub(r"[^0-9A-Za-zぁ-んァ-ヶ一-龠々ー]+", "", str(text)).lower()


def _accepted_drafts() -> list[dict[str, Any]]:
    primary = _read(MAIN_DRAFT_PATH)["drafts"]
    replacement = _read(REPLACEMENT_PATH)["draft"]
    accepted = [draft for draft in primary if draft["draft_id"] not in HOLD_IDS]
    accepted.append(replacement)
    return accepted


def build_report() -> dict[str, Any]:
    questions = _index(_read(BANK_DIR / "questions.json"))
    answers = _index(_read(BANK_DIR / "answers.json"))
    explanations = _index(_read(BANK_DIR / "explanations.json"))
    tags = _index(_read(BANK_DIR / "question_tags.json"))
    nodes = {
        str(node["knowledge_node_id"]): node
        for node in _read(BANK_DIR / "knowledge_nodes.json")
    }

    bank_ids = set(questions)
    hard_errors: list[str] = []
    warnings: list[str] = []
    rows: list[dict[str, Any]] = []

    accepted = _accepted_drafts()
    accepted_ids = [draft["draft_id"] for draft in accepted]
    if len(accepted) != 12 or len(set(accepted_ids)) != 12:
        hard_errors.append(f"accepted draft count/id uniqueness invalid: {accepted_ids}")

    target_nodes = [str(draft["target_node_id"]) for draft in accepted]
    if len(set(target_nodes)) != len(target_nodes):
        hard_errors.append("accepted drafts contain duplicate target Knowledge Nodes")
    if "KN0779" in target_nodes:
        hard_errors.append("KN0779 must remain excluded")

    normalized_bank = {
        qid: _normalize(question.get("question_text", ""))
        for qid, question in questions.items()
    }

    for draft in accepted:
        draft_id = str(draft["draft_id"])
        node_id = str(draft["target_node_id"])
        ref_ids = [str(value) for value in draft.get("reference_question_ids", [])]
        node = nodes.get(node_id)
        if node is None:
            hard_errors.append(f"{draft_id}: missing target node {node_id}")
            continue

        registry_qids = [str(value) for value in node.get("question_ids", [])]
        if len(registry_qids) != 1:
            hard_errors.append(
                f"{draft_id}: singleton-first target {node_id} currently has {registry_qids}"
            )
        if set(ref_ids) != set(registry_qids):
            hard_errors.append(
                f"{draft_id}: reference ids {ref_ids} != registry ids {registry_qids}"
            )

        missing_store_ids = [
            qid for qid in ref_ids
            if qid not in bank_ids or qid not in answers or qid not in explanations or qid not in tags
        ]
        if missing_store_ids:
            hard_errors.append(f"{draft_id}: references missing in four stores: {missing_store_ids}")
            continue

        ref_qid = ref_ids[0]
        ref_question = questions[ref_qid]
        ref_tag = tags[ref_qid]
        actual_small = int(ref_question["category_small"])
        actual_large = str(ref_question["category_large"])
        proposed_small = int(draft["proposed_category_small"])
        proposed_large = str(draft["proposed_category_large"])
        category_matches = proposed_small == actual_small and proposed_large == actual_large
        if not category_matches:
            hard_errors.append(
                f"{draft_id}: proposed category {proposed_large}-{proposed_small} "
                f"!= reference {ref_qid} category {actual_large}-{actual_small}"
            )

        if str(ref_tag.get("knowledge_node_id")) != node_id:
            hard_errors.append(
                f"{draft_id}: {ref_qid} tag node {ref_tag.get('knowledge_node_id')} != {node_id}"
            )

        draft_norm = _normalize(draft["question_text"])
        exact_duplicates = [qid for qid, norm in normalized_bank.items() if norm == draft_norm]
        if exact_duplicates:
            hard_errors.append(f"{draft_id}: exact normalized stem duplicate {exact_duplicates}")

        similarities = sorted(
            (
                (SequenceMatcher(None, draft_norm, norm).ratio(), qid)
                for qid, norm in normalized_bank.items()
                if norm
            ),
            reverse=True,
        )[:5]
        near = [
            {"qid": qid, "ratio": round(ratio, 4)}
            for ratio, qid in similarities
            if ratio >= 0.78
        ]
        if near:
            warnings.append(f"{draft_id}: inspect near-similar stems {near}")

        rows.append(
            {
                "draft_id": draft_id,
                "target_node_id": node_id,
                "node_status": node.get("status"),
                "reference_qid": ref_qid,
                "reference_category": f"{actual_large}-{actual_small}",
                "reference_task": ref_tag.get("task"),
                "reference_primary_ability": ref_tag.get("primary_ability"),
                "reference_level": ref_tag.get("level"),
                "reference_safety": ref_tag.get("safety"),
                "draft_task": draft.get("proposed_task"),
                "draft_primary_ability": draft.get("primary_ability"),
                "draft_level": draft.get("level"),
                "draft_safety": draft.get("safety"),
                "category_matches": category_matches,
                "near_stem_matches": near,
            }
        )

    return {
        "accepted_count": len(accepted),
        "hold_ids": sorted(HOLD_IDS),
        "replacement_id": REPLACEMENT_ID,
        "hard_errors": hard_errors,
        "warnings": warnings,
        "rows": rows,
    }


def main() -> int:
    report = build_report()
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if report["hard_errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
