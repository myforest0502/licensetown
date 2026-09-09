"""Fail-closed staging validator for Question Bank 2000 production Lot 02."""
from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from collections import Counter, defaultdict
from difflib import SequenceMatcher
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BANK = ROOT / "data" / "question_bank"
ROSTER = ROOT / "reports" / "question_bank_2000_lot02_targets_v01.json"
STAGING = ROOT / "staging" / "question_bank_2000_lot02_v01.json"
PROTECTED = (
    "questions.json",
    "answers.json",
    "explanations.json",
    "question_tags.json",
    "knowledge_nodes.json",
    "bank_manifest.json",
    "schema/question_bank_schema_v1.json",
    "knowledge_node_canonical_map.json",
    "strong_different_question_pairs.json",
)
TASK_PRIMARY = {
    "assessment_selection":"MEASURE",
    "device_selection":"PRESCRIBE",
    "fact_recall":"KNOW",
    "finding_interpretation":"INTERPRET",
    "functional_goal_decision":"DECIDE",
    "intervention_selection":"PRESCRIBE",
    "prognosis_prediction":"PREDICT",
    "safety_priority":"DECIDE",
}
CATEGORY_QUOTA = {8:8,9:6,11:5,12:5,14:4,16:5,17:7,18:8}
TASK_QUOTA = {
    "assessment_selection":9,
    "device_selection":2,
    "fact_recall":1,
    "finding_interpretation":14,
    "functional_goal_decision":4,
    "intervention_selection":9,
    "prognosis_prediction":3,
    "safety_priority":6,
}
LEVEL_QUOTA = {1:1,2:16,3:20,4:11}
SLOT_QUOTA = {"singleton_second":32,"multi_reinforcement":12,"new_node":4}
SAFETY_AUGMENT = 12
MIN_STRONG = 41
ACCEPTED_COUNT = 48
START_NEW_NODE = 1543
BASE_COUNT = 1809
BASE_VERSION = "2026-09-b15"
INTEGRATED_START = 1810
INTEGRATED_END = 1857
INTEGRATED_VERSION = "2026-09-b16"
NEAR_THRESHOLD = 0.65
HARD_NEAR_THRESHOLD = 0.78


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def normalize(text: str) -> str:
    value = unicodedata.normalize("NFKC", str(text or "")).lower()
    return re.sub(r"[^0-9a-zぁ-んァ-ヶ一-龠々ー]+", "", value)


def fingerprint(value) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def draft_fingerprint(draft: dict) -> str:
    return fingerprint({k:v for k,v in draft.items() if k != "reviewed_sha256"})


def file_fingerprint(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def _canonical_map() -> dict[str,str]:
    mapping = {}
    for row in read(BANK / "knowledge_node_canonical_map.json"):
        canonical = str(row["canonical_node_id"])
        mapping[canonical] = canonical
        for alias in row.get("alias_node_ids", []):
            mapping[str(alias)] = canonical
    return mapping


def build_report(payload: dict | None = None, *, require_seals: bool = True) -> dict:
    payload = read(STAGING) if payload is None else payload
    errors: list[str] = []
    warnings: list[str] = []
    rows: list[dict] = []
    def check(condition: bool, message: str):
        if not condition:
            errors.append(message)

    manifest = read(BANK / "bank_manifest.json")
    questions = read(BANK / "questions.json")
    answers = read(BANK / "answers.json")
    explanations = read(BANK / "explanations.json")
    tags = read(BANK / "question_tags.json")
    nodes = read(BANK / "knowledge_nodes.json")
    maps = {
        "questions": {r["id"]:r for r in questions},
        "answers": {r["id"]:r for r in answers},
        "explanations": {r["id"]:r for r in explanations},
        "question_tags": {r["id"]:r for r in tags},
    }
    integrated_ids = [f"Q{number}" for number in range(INTEGRATED_START, INTEGRATED_END + 1)]
    integrated_count = sum(qid in maps["questions"] for qid in integrated_ids)
    check(integrated_count in (0, ACCEPTED_COUNT), f"partial formal integration: {integrated_count}/{ACCEPTED_COUNT}")
    integrated = integrated_count == ACCEPTED_COUNT
    if integrated:
        check(manifest.get("question_count", 0) >= INTEGRATED_END,
              "formal integrated count is below 1857")
        check(manifest.get("last_question_number") == manifest.get("question_count"),
              "formal integrated range/count mismatch")
        if manifest.get("question_count") == INTEGRATED_END:
            check(manifest.get("bank_version") == INTEGRATED_VERSION,
                  "formal integrated version is not 2026-09-b16")
    else:
        check(manifest.get("question_count") == BASE_COUNT, "formal baseline count is not 1809")
        check(manifest.get("last_question_number") == BASE_COUNT, "formal baseline range is not Q1-Q1809")
        check(manifest.get("bank_version") == BASE_VERSION, "formal baseline version is not 2026-09-b15")
    node_index = {r["knowledge_node_id"]:r for r in nodes}
    canon = _canonical_map()
    canonical = lambda node_id: canon.get(str(node_id), str(node_id))
    formal_groups = defaultdict(list)
    for tag in tags:
        formal_groups[canonical(tag["knowledge_node_id"])].append(tag["id"])
    for qids in formal_groups.values():
        qids.sort(key=lambda q:int(q[1:]))

    roster = read(ROSTER)
    roster_by_id = {r["lot_target_id"]:r for r in roster["existing_node_targets"]}
    expected_new_categories = Counter(int(r["category_small"]) for r in roster["new_node_reservations"])

    check(payload.get("batch") == "question_bank_2000_production_lot02_v01", "batch id mismatch")
    check(payload.get("status") == "staging_only", "status must be staging_only")
    for key in ("q_ids_reserved","production_write","db_write"):
        check(payload.get(key) is False, f"{key} must be false")
    if require_seals:
        check(payload.get("formal_hash_format") == "sha256-lf-normalized-v1", "formal hash format invalid")
        hashes = payload.get("formal_input_sha256", {})
        check(set(hashes) == set(PROTECTED), "formal protected hash set incomplete")
        protected = (
            ("knowledge_node_canonical_map.json", "strong_different_question_pairs.json")
            if integrated else PROTECTED
        )
        for name in protected:
            check(hashes.get(name) == file_fingerprint(BANK / name), f"formal snapshot changed: {name}")

    drafts = payload.get("drafts", [])
    check(len(drafts) == ACCEPTED_COUNT, f"accepted draft count must be {ACCEPTED_COUNT}, got {len(drafts)}")
    ids = [str(d.get("draft_id")) for d in drafts]
    check(len(set(ids)) == len(ids), "duplicate draft IDs")
    check(all(d.get("status") == "accepted" for d in drafts), "all drafts must be accepted before staging seal")

    category_count = Counter()
    task_count = Counter()
    level_count = Counter()
    slot_count = Counter()
    safety_count = Counter()
    strong_possible = 0
    new_categories = Counter()
    formal_stems = {qid:normalize(row["question_text"]) for qid,row in maps["questions"].items()}
    candidate_norms: dict[str,str] = {}
    normalized_node_labels = {normalize(r.get("label", "")): r["knowledge_node_id"] for r in nodes if normalize(r.get("label", ""))}

    new_node_offset = 0
    for draft_offset, d in enumerate(drafts):
        did = str(d.get("draft_id") or "?")
        prefix = f"{did}: "
        slot = str(d.get("slot_type") or "")
        category = d.get("proposed_category_small")
        task = str(d.get("proposed_task") or "")
        ability = str(d.get("primary_ability") or "")
        level = d.get("level")
        safety = str(d.get("safety") or "")
        category_count[category] += 1
        task_count[task] += 1
        level_count[level] += 1
        slot_count[slot] += 1
        safety_count[safety] += 1

        forbidden = {"id","qid","q_id","question_id","reserved_qid","new_question_id","management_code"}
        check(not forbidden.intersection(d), prefix + "formal Q ID allocation forbidden in staging")
        check(d.get("source") == "original", prefix + "source must be original")
        check(task in TASK_PRIMARY and TASK_PRIMARY.get(task) == ability, prefix + "task/primary ability mismatch")
        check(level in {1,2,3,4}, prefix + "invalid level")
        check(safety in {"none","moderate","critical"}, prefix + "invalid safety")
        if task == "safety_priority":
            check(safety in {"moderate","critical"}, prefix + "safety_priority cannot have safety=none")

        stem = d.get("question_text", "")
        check(isinstance(stem, str) and bool(stem.strip()), prefix + "question text required")
        if isinstance(stem, str):
            check(len(stem) <= 400, prefix + "stem exceeds hard 400-character ceiling")
            if len(stem) > 300:
                check(bool(d.get("length_exception_reason")), prefix + "stem >300 requires length_exception_reason")
        choices = d.get("choices", {})
        reasons = d.get("choice_explanations", {})
        choice_ok = isinstance(choices, dict) and isinstance(reasons, dict) and set(choices) == set(reasons) == set("12345")
        check(choice_ok, prefix + "five choices and five choice explanations required")
        if choice_ok:
            check(all(isinstance(v,str) and v.strip() for v in [*choices.values(),*reasons.values()]), prefix + "blank choice or explanation")
            check(len({normalize(v) for v in choices.values()}) == 5, prefix + "duplicate choice text")
        answer = d.get("correct_choices", [])
        check(isinstance(answer,list) and len(answer) == 1 and str(answer[0]) in "12345" and str(answer[0]) in choices, prefix + "single best answer required")
        check(bool(str(d.get("explanation") or "").strip()), prefix + "correct explanation required")
        check(bool(str(d.get("clinical_intent") or "").strip()), prefix + "clinical intent required")

        evidence = d.get("evidence", [])
        check(isinstance(evidence,list) and bool(evidence), prefix + "medical evidence required")
        if isinstance(evidence,list):
            check(all(isinstance(e,dict) and str(e.get("url","")).startswith("https://") and bool(str(e.get("support","")).strip()) for e in evidence), prefix + "evidence URL/support invalid")
        review = d.get("semantic_review", {})
        check(isinstance(review,dict) and review.get("decision") == "accepted", prefix + "semantic review not accepted")
        for key in ("candidate_demand","why_not_same_demand","reviewer","reviewed_on"):
            check(bool(str(review.get(key,"")).strip()), prefix + f"semantic review missing {key}")
        if slot != "new_node":
            check(bool(str(review.get("reference_demand","")).strip()), prefix + "reference demand required")
        if require_seals:
            check(d.get("reviewed_sha256") == draft_fingerprint(d), prefix + "content changed after semantic review seal")

        norm = normalize(stem)
        candidate_norms[did] = norm
        integrated_qid = f"Q{INTEGRATED_START + draft_offset}"
        comparison_stems = {
            qid: text for qid, text in formal_stems.items()
            if not integrated or qid != integrated_qid
        }
        exact = [qid for qid,text in comparison_stems.items() if text and text == norm]
        check(not exact, prefix + f"exact formal duplicate: {exact}")
        if norm:
            ranked = sorted(((SequenceMatcher(None,norm,text,autojunk=False).ratio(),qid) for qid,text in comparison_stems.items() if text), reverse=True)[:5]
            hard_near = [(qid,score) for score,qid in ranked if score >= HARD_NEAR_THRESHOLD]
            if hard_near:
                reviewed_related = {str(x.get("qid")) for x in review.get("related_formal_questions", []) if isinstance(x,dict)}
                unresolved = [qid for qid,_ in hard_near if qid not in reviewed_related]
                check(not unresolved, prefix + f"high-similarity formal stems require explicit semantic review: {unresolved}")
            warnings.extend(prefix + f"near formal {qid}={score:.3f}" for score,qid in ranked if score >= NEAR_THRESHOLD)

        if slot in {"singleton_second","multi_reinforcement"}:
            target = roster_by_id.get(did)
            check(target is not None, prefix + "draft not in reviewed existing-Node roster")
            if target:
                node_id = str(d.get("target_node_id") or "")
                check(node_id == target["canonical_node_id"], prefix + "target Node changed from roster")
                check(category == target["category_small"], prefix + "category changed from roster")
                refs = [str(x) for x in d.get("reference_question_ids", [])]
                check(refs == target["question_ids"], prefix + "reference membership changed from roster")
                expected_group = list(target["question_ids"]) + ([integrated_qid] if integrated else [])
                check(formal_groups.get(canonical(node_id), []) == expected_group,
                      prefix + "formal canonical Node membership changed")
                check(all(qid in maps["questions"] and qid in maps["answers"] and qid in maps["explanations"] and qid in maps["question_tags"] for qid in refs), prefix + "reference missing from four formal stores")
                existing_demands = {(str(x["task"]),str(x["primary_ability"])) for x in target.get("existing_demands", [])}
                candidate_demand = (task, ability)
                check(candidate_demand not in existing_demands, prefix + "candidate demand already exists in target Node")
                if candidate_demand not in existing_demands:
                    strong_possible += 1
                if slot == "singleton_second":
                    check(len(refs) == 1, prefix + "singleton target must have exactly one formal reference")
                else:
                    check(len(refs) > 1, prefix + "multi target must have multiple formal references")
            check(d.get("target_node_label") == (target or {}).get("label"), prefix + "target Node label changed from roster")
        elif slot == "new_node":
            new_categories[category] += 1
            check(d.get("target_node_id") is None, prefix + "new Node ID must not be allocated in staging")
            check(d.get("reference_question_ids") == [], prefix + "new Node staging slot cannot have formal references")
            label = str(d.get("target_node_label") or "").strip()
            check(bool(label), prefix + "proposed new Node label required")
            if label:
                label_norm = normalize(label)
                allocated_node_id = f"KN{START_NEW_NODE + new_node_offset:04d}"
                duplicate_node = normalized_node_labels.get(label_norm)
                check(not duplicate_node or (integrated and duplicate_node == allocated_node_id),
                      prefix + f"new Node label duplicates existing Node {duplicate_node}")
            new_node_offset += 1
            collision = d.get("new_node_collision_review", {})
            check(isinstance(collision,dict) and collision.get("decision") == "accepted_new_node", prefix + "new Node collision review required")
            check(bool(str(collision.get("why_existing_nodes_insufficient","")).strip()), prefix + "new Node collision rationale required")
        else:
            check(False, prefix + f"invalid slot_type {slot!r}")

        if integrated:
            check(all(integrated_qid in mapping for mapping in maps.values()),
                  prefix + "integrated Q missing from formal stores")
            if all(integrated_qid in mapping for mapping in maps.values()):
                check(maps["questions"][integrated_qid].get("question_text") == d.get("question_text"),
                      prefix + "formal question differs from sealed staging")
                formal_tag = maps["question_tags"][integrated_qid]
                check((formal_tag.get("task"), formal_tag.get("primary_ability")) == (task, ability),
                      prefix + "formal demand differs from sealed staging")

        rows.append({
            "draft_id":did,
            "slot_type":slot,
            "category":category,
            "task":task,
            "primary_ability":ability,
            "level":level,
            "safety":safety,
        })

    for left,right in combinations(drafts,2):
        a = candidate_norms.get(str(left.get("draft_id")),"")
        b = candidate_norms.get(str(right.get("draft_id")),"")
        if not a or not b:
            continue
        if a == b:
            errors.append(f"candidate exact duplicate: {left.get('draft_id')} / {right.get('draft_id')}")
            continue
        score = SequenceMatcher(None,a,b,autojunk=False).ratio()
        if score >= HARD_NEAR_THRESHOLD:
            errors.append(f"candidate high-similarity pair requires rewrite/review: {left.get('draft_id')} / {right.get('draft_id')} = {score:.3f}")
        elif score >= NEAR_THRESHOLD:
            warnings.append(f"candidate near pair: {left.get('draft_id')} / {right.get('draft_id')} = {score:.3f}")

    check(category_count == Counter(CATEGORY_QUOTA), f"category quota mismatch: {dict(category_count)}")
    check(task_count == Counter(TASK_QUOTA), f"task quota mismatch: {dict(task_count)}")
    check(level_count == Counter(LEVEL_QUOTA), f"level quota mismatch: {dict(level_count)}")
    check(slot_count == Counter(SLOT_QUOTA), f"slot quota mismatch: {dict(slot_count)}")
    check(safety_count["moderate"] + safety_count["critical"] == SAFETY_AUGMENT, f"Safety augmentation must be exactly {SAFETY_AUGMENT}: {dict(safety_count)}")
    check(new_categories == expected_new_categories, f"new Node category reservation mismatch: {dict(new_categories)}")
    check(strong_possible >= MIN_STRONG, f"structural strong formations {strong_possible} < {MIN_STRONG}")

    return {
        "accepted_count":len(drafts),
        "hard_errors":errors,
        "warnings":warnings,
        "category_counts":dict(category_count),
        "task_counts":dict(task_count),
        "level_counts":dict(level_count),
        "slot_counts":dict(slot_count),
        "safety_counts":dict(safety_count),
        "structural_strong_formations":strong_possible,
        "lifecycle":"integrated" if integrated else "staging",
        "integrated_count":integrated_count,
        "formal_count":manifest.get("question_count"),
        "rows":rows,
    }


def main() -> int:
    if not STAGING.exists():
        print(json.dumps({"status":"not_authored","expected":str(STAGING.relative_to(ROOT))},ensure_ascii=False))
        return 2
    report = build_report()
    print(json.dumps(report,ensure_ascii=False,indent=2))
    return 1 if report["hard_errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
