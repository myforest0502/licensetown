"""Fail-closed authoring-completeness validator for one Lot02 8-draft chunk.

Passing a chunk never permits integration, Q-ID allocation, Node-ID allocation,
sealing, or formal writes. Final 48-question quotas are enforced by the Lot02
final validator.
"""
from __future__ import annotations

import argparse
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHUNK_DIR = ROOT / "staging" / "question_bank_2000_lot02_chunks_v01"
FORBIDDEN_ID_FIELDS = {"id", "qid", "q_id", "question_id", "reserved_qid", "new_question_id", "management_code"}
TASK_PRIMARY = {
    "assessment_selection": "MEASURE",
    "device_selection": "PRESCRIBE",
    "fact_recall": "KNOW",
    "finding_interpretation": "INTERPRET",
    "functional_goal_decision": "DECIDE",
    "intervention_selection": "PRESCRIBE",
    "prognosis_prediction": "PREDICT",
    "safety_priority": "DECIDE",
}


def normalize(text: str) -> str:
    value = unicodedata.normalize("NFKC", str(text or "")).lower()
    return re.sub(r"[^0-9a-zぁ-んァ-ヶ一-龠々ー]+", "", value)


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def build_report(payload: dict) -> dict:
    errors: list[str] = []
    warnings: list[str] = []

    def check(condition: bool, message: str):
        if not condition:
            errors.append(message)

    check(payload.get("lot") == "question_bank_2000_production_lot02_v01", "lot id mismatch")
    check(payload.get("status") == "completed_chunk", "chunk status must be completed_chunk")
    check(payload.get("formal_baseline") == "Q1-Q1809", "formal baseline mismatch")
    for key in ("q_ids_reserved", "production_write", "db_write"):
        check(payload.get(key) is False, f"{key} must be false")

    drafts = payload.get("drafts", [])
    check(isinstance(drafts, list) and len(drafts) == 8,
          f"chunk must contain exactly 8 drafts, got {len(drafts) if isinstance(drafts, list) else 'non-list'}")
    draft_ids = [str(d.get("draft_id")) for d in drafts if isinstance(d, dict)]
    check(len(draft_ids) == len(set(draft_ids)), "duplicate draft IDs in chunk")
    stem_norms: dict[str, str] = {}

    for d in drafts if isinstance(drafts, list) else []:
        if not isinstance(d, dict):
            errors.append("non-object draft")
            continue
        did = str(d.get("draft_id") or "?")
        p = f"{did}: "
        check(d.get("status") in {"authoring", "accepted"}, p + "invalid draft status")
        check(not FORBIDDEN_ID_FIELDS.intersection(d), p + "formal Q ID allocation forbidden")
        check(d.get("source") == "original", p + "source must be original")
        task = str(d.get("proposed_task") or "")
        ability = str(d.get("primary_ability") or "")
        check(task in TASK_PRIMARY and TASK_PRIMARY.get(task) == ability, p + "task/primary ability mismatch")
        check(d.get("level") in {1, 2, 3, 4}, p + "invalid level")
        safety = str(d.get("safety") or "")
        check(safety in {"none", "moderate", "critical"}, p + "invalid safety")
        if task == "safety_priority":
            check(safety in {"moderate", "critical"}, p + "safety_priority cannot have safety=none")

        stem = str(d.get("question_text") or "")
        check(bool(stem.strip()), p + "question text required")
        check(len(stem) <= 400, p + "stem exceeds hard 400-character ceiling")
        if len(stem) > 300:
            check(bool(str(d.get("length_exception_reason") or "").strip()), p + "stem >300 requires length_exception_reason")
        stem_norms[did] = normalize(stem)

        choices = d.get("choices", {})
        reasons = d.get("choice_explanations", {})
        choice_ok = isinstance(choices, dict) and isinstance(reasons, dict) and set(choices) == set(reasons) == set("12345")
        check(choice_ok, p + "five choices and five choice explanations required")
        if choice_ok:
            check(all(isinstance(v, str) and v.strip() for v in [*choices.values(), *reasons.values()]), p + "blank choice or explanation")
            check(len({normalize(v) for v in choices.values()}) == 5, p + "duplicate choice text")
        answer = d.get("correct_choices", [])
        check(isinstance(answer, list) and len(answer) == 1 and str(answer[0]) in "12345", p + "single best answer required")
        check(bool(str(d.get("explanation") or "").strip()), p + "correct explanation required")
        check(bool(str(d.get("clinical_intent") or "").strip()), p + "clinical intent required")

        evidence = d.get("evidence", [])
        check(isinstance(evidence, list) and bool(evidence), p + "medical evidence required")
        if isinstance(evidence, list):
            check(all(isinstance(e, dict) and str(e.get("url", "")).startswith("https://") and bool(str(e.get("support", "")).strip()) for e in evidence), p + "evidence URL/support invalid")

        review = d.get("semantic_review", {})
        check(isinstance(review, dict) and review.get("decision") == "accepted", p + "semantic review not accepted")
        if isinstance(review, dict):
            for key in ("candidate_demand", "why_not_same_demand", "reviewer", "reviewed_on"):
                check(bool(str(review.get(key, "")).strip()), p + f"semantic review missing {key}")
            check(isinstance(review.get("expert_signoff"), bool), p + "expert_signoff must be an explicit boolean")

        slot = str(d.get("slot_type") or "")
        if slot in {"singleton_second", "multi_reinforcement"}:
            check(bool(str(d.get("target_node_id") or "").strip()), p + "existing Node target required")
            existing = {(str(x.get("task")), str(x.get("primary_ability"))) for x in d.get("existing_demands", []) if isinstance(x, dict)}
            check((task, ability) not in existing, p + "candidate demand duplicates existing Node demand")
            check(bool(d.get("reference_question_ids")), p + "formal reference required")
        elif slot == "new_node":
            check(d.get("target_node_id") is None, p + "new Node ID must not be allocated in chunk")
            check(d.get("reference_question_ids") == [], p + "new Node chunk must not claim formal references")
            check(bool(str(d.get("target_node_label") or "").strip()), p + "new Node label proposal required")
            collision = d.get("new_node_collision_review", {})
            check(isinstance(collision, dict) and collision.get("decision") == "accepted_new_node", p + "new Node collision review required")
            if isinstance(collision, dict):
                check(bool(str(collision.get("why_existing_nodes_insufficient") or "").strip()), p + "new Node collision rationale required")
        else:
            check(False, p + f"invalid slot_type {slot!r}")

    ids = list(stem_norms)
    for i, left in enumerate(ids):
        for right in ids[i + 1:]:
            if stem_norms[left] and stem_norms[left] == stem_norms[right]:
                errors.append(f"exact duplicate stems inside chunk: {left}, {right}")

    return {"hard_errors": errors, "warnings": warnings, "draft_count": len(drafts) if isinstance(drafts, list) else 0}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("chunk", type=int, choices=range(1, 7))
    args = parser.parse_args()
    path = CHUNK_DIR / f"chunk_{args.chunk:02d}.json"
    report = build_report(read(path))
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if report["hard_errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
