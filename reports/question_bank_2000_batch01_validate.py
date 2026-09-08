"""Read-only validation for Question Bank 2000 Batch 01 staging/formal lifecycle."""
from __future__ import annotations

import copy
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
CATEGORY_CORRECTIONS_PATH = STAGING_DIR / "question_bank_2000_batch01_category_corrections_v01.json"
SEMANTIC_REPLACEMENTS_PATH = STAGING_DIR / "question_bank_2000_batch01_semantic_replacements_v01.json"

HOLD_IDS = {"B01-05"}
REPLACEMENT_ID = "B01-R1"
START_Q = 1738
END_Q = 1749
LETTERS = "ABCDE"


def _read(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _index(records: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {str(record["id"]): record for record in records}


def _normalize(text: str) -> str:
    return re.sub(r"[^0-9A-Za-zぁ-んァ-ヶ一-龠々ー]+", "", str(text)).lower()


def _choice_map(values: dict[str, str]) -> dict[str, str]:
    mapped: dict[str, str] = {}
    for index, letter in enumerate(LETTERS, start=1):
        value = values.get(str(index), values.get(letter))
        if value is None:
            raise ValueError(f"missing choice {index}/{letter}")
        mapped[letter] = str(value)
    return mapped


def _correct_letters(values: list[str]) -> list[str]:
    result: list[str] = []
    for value in values:
        text = str(value)
        if text in LETTERS:
            result.append(text)
        elif text.isdigit() and 1 <= int(text) <= 5:
            result.append(LETTERS[int(text) - 1])
        else:
            raise ValueError(f"unsupported correct choice {text}")
    return result


def _accepted_drafts() -> list[dict[str, Any]]:
    primary = _read(MAIN_DRAFT_PATH)["drafts"]
    replacement = _read(REPLACEMENT_PATH)["draft"]
    corrections = _read(CATEGORY_CORRECTIONS_PATH).get("corrections", {})
    semantic = _read(SEMANTIC_REPLACEMENTS_PATH).get("replacements", {})

    accepted = [copy.deepcopy(draft) for draft in primary if draft["draft_id"] not in HOLD_IDS]
    accepted.append(copy.deepcopy(replacement))

    for index, draft in enumerate(accepted):
        draft_id = str(draft["draft_id"])
        if draft_id in semantic:
            accepted[index] = copy.deepcopy(semantic[draft_id])
            accepted[index]["semantic_replacement_applied"] = True

    for draft in accepted:
        correction = corrections.get(str(draft["draft_id"]))
        if correction and not draft.get("semantic_replacement_applied"):
            draft["proposed_category_large"] = correction["category_large"]
            draft["proposed_category_small"] = correction["category_small"]
            draft["category_correction_applied"] = True
    return accepted


def build_report() -> dict[str, Any]:
    questions = _index(_read(BANK_DIR / "questions.json"))
    answers = _index(_read(BANK_DIR / "answers.json"))
    explanations = _index(_read(BANK_DIR / "explanations.json"))
    tags = _index(_read(BANK_DIR / "question_tags.json"))
    nodes = {str(node["knowledge_node_id"]): node for node in _read(BANK_DIR / "knowledge_nodes.json")}

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

    normalized_bank = {qid: _normalize(question.get("question_text", "")) for qid, question in questions.items()}
    integrated_count = 0

    for offset, draft in enumerate(accepted):
        draft_id = str(draft["draft_id"])
        node_id = str(draft["target_node_id"])
        expected_qid = f"Q{START_Q + offset}"
        integrated = expected_qid in bank_ids
        if integrated:
            integrated_count += 1

        ref_ids = [str(value) for value in draft.get("reference_question_ids", [])]
        node = nodes.get(node_id)
        if node is None:
            hard_errors.append(f"{draft_id}: missing target node {node_id}")
            continue
        if len(ref_ids) != 1:
            hard_errors.append(f"{draft_id}: expected one singleton reference, got {ref_ids}")
            continue

        ref_qid = ref_ids[0]
        registry_qids = [str(value) for value in node.get("question_ids", [])]
        expected_registry = [ref_qid, expected_qid] if integrated else [ref_qid]
        expected_status = "confirmed_shared" if integrated else "singleton_initial"
        if registry_qids != expected_registry:
            hard_errors.append(f"{draft_id}: node {node_id} question_ids {registry_qids} != expected {expected_registry}")
        if str(node.get("status")) != expected_status:
            hard_errors.append(f"{draft_id}: node {node_id} status {node.get('status')} != expected {expected_status}")

        reference_missing = [qid for qid in ref_ids if qid not in bank_ids or qid not in answers or qid not in explanations or qid not in tags]
        if reference_missing:
            hard_errors.append(f"{draft_id}: references missing in four stores: {reference_missing}")
            continue

        ref_question = questions[ref_qid]
        ref_tag = tags[ref_qid]
        actual_small = int(ref_question["category_small"])
        actual_large = str(ref_question["category_large"])
        proposed_small = int(draft["proposed_category_small"])
        proposed_large = str(draft["proposed_category_large"])
        category_matches = proposed_small == actual_small and proposed_large == actual_large
        if not category_matches:
            hard_errors.append(f"{draft_id}: effective category {proposed_large}-{proposed_small} != reference {ref_qid} category {actual_large}-{actual_small}")
        if str(ref_tag.get("knowledge_node_id")) != node_id:
            hard_errors.append(f"{draft_id}: {ref_qid} tag node {ref_tag.get('knowledge_node_id')} != {node_id}")

        draft_norm = _normalize(draft["question_text"])
        excluded_qids = {expected_qid} if integrated else set()
        exact_duplicates = [qid for qid, norm in normalized_bank.items() if qid not in excluded_qids and norm == draft_norm]
        if exact_duplicates:
            hard_errors.append(f"{draft_id}: exact normalized stem duplicate {exact_duplicates}")

        if integrated:
            integrated_missing = [expected_qid for store in (questions, answers, explanations, tags) if expected_qid not in store]
            if integrated_missing:
                hard_errors.append(f"{draft_id}: {expected_qid} missing from one or more formal stores")
            else:
                question = questions[expected_qid]
                answer = answers[expected_qid]
                explanation = explanations[expected_qid]
                tag = tags[expected_qid]
                expected_choices = _choice_map(draft["choices"])
                expected_correct = _correct_letters(draft["correct_choices"])
                expected_choice_explanations = _choice_map(draft["choice_explanations"])

                if str(question.get("category_large")) != proposed_large or int(question.get("category_small")) != proposed_small:
                    hard_errors.append(f"{draft_id}: {expected_qid} formal category mismatch")
                if _normalize(question.get("question_text", "")) != draft_norm:
                    hard_errors.append(f"{draft_id}: {expected_qid} formal stem differs from accepted draft")
                if question.get("choices") != expected_choices:
                    hard_errors.append(f"{draft_id}: {expected_qid} formal choices differ from accepted draft")
                if answer.get("display_answer") != expected_correct[0] or answer.get("accepted_answer_sets") != [expected_correct]:
                    hard_errors.append(f"{draft_id}: {expected_qid} formal answer differs from accepted draft")
                if explanation.get("explanation") != draft.get("explanation") or explanation.get("choice_explanations") != expected_choice_explanations:
                    hard_errors.append(f"{draft_id}: {expected_qid} formal explanation differs from accepted draft")
                expected_tag_values = {
                    "knowledge_node_id": node_id,
                    "task": draft.get("proposed_task"),
                    "primary_ability": draft.get("primary_ability"),
                    "secondary_ability": draft.get("secondary_ability"),
                    "level": int(draft.get("level")),
                    "safety": draft.get("safety"),
                    "source": "original",
                }
                for key, expected_value in expected_tag_values.items():
                    if tag.get(key) != expected_value:
                        hard_errors.append(f"{draft_id}: {expected_qid} tag {key}={tag.get(key)!r} != {expected_value!r}")

        similarity_source = [(qid, norm) for qid, norm in normalized_bank.items() if qid not in excluded_qids and norm]
        similarities = sorted(((SequenceMatcher(None, draft_norm, norm).ratio(), qid) for qid, norm in similarity_source), reverse=True)[:5]
        near = [{"qid": qid, "ratio": round(ratio, 4)} for ratio, qid in similarities if ratio >= 0.78]
        if near:
            warnings.append(f"{draft_id}: inspect near-similar stems {near}")

        rows.append({
            "draft_id": draft_id,
            "target_node_id": node_id,
            "node_status": node.get("status"),
            "reference_qid": ref_qid,
            "expected_integrated_qid": expected_qid,
            "integrated": integrated,
            "reference_question_text": str(ref_question.get("question_text", "")),
            "reference_category": f"{actual_large}-{actual_small}",
            "effective_draft_category": f"{proposed_large}-{proposed_small}",
            "category_correction_applied": bool(draft.get("category_correction_applied")),
            "semantic_replacement_applied": bool(draft.get("semantic_replacement_applied")),
            "reference_task": ref_tag.get("task"),
            "reference_primary_ability": ref_tag.get("primary_ability"),
            "reference_level": ref_tag.get("level"),
            "reference_safety": ref_tag.get("safety"),
            "draft_question_text": str(draft.get("question_text", "")),
            "draft_task": draft.get("proposed_task"),
            "draft_primary_ability": draft.get("primary_ability"),
            "draft_level": draft.get("level"),
            "draft_safety": draft.get("safety"),
            "category_matches": category_matches,
            "near_stem_matches": near,
        })

    if integrated_count not in (0, len(accepted)):
        hard_errors.append(f"partial formal integration detected: {integrated_count}/{len(accepted)}")

    return {
        "accepted_count": len(accepted),
        "integrated_count": integrated_count,
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
