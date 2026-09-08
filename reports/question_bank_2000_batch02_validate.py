"""Read-only Batch02 staging/formal lifecycle audit.

Content hashes bind the editorial review to the reviewed staging inputs. Before
integration all protected formal inputs must match that snapshot. After complete
integration, the expected seven formal files may change only through the exact
staging-to-formal contract while immutable canonical/strong-pair inputs must stay
unchanged.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from difflib import SequenceMatcher
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from knowledge_node_canonical import canonicalize_knowledge_node_id as canonical

BANK = ROOT / "data/question_bank"
STAGING = ROOT / "staging/question_bank_2000_batch02_v01.json"
STORES = ("questions", "answers", "explanations", "question_tags")
PROTECTED = tuple(f"{name}.json" for name in STORES) + (
    "knowledge_nodes.json", "bank_manifest.json", "schema/question_bank_schema_v1.json",
    "knowledge_node_canonical_map.json", "strong_different_question_pairs.json",
)
IMMUTABLE_AFTER_INTEGRATION = (
    "knowledge_node_canonical_map.json", "strong_different_question_pairs.json",
)
TASK_PRIMARY = {
    "assessment_selection": "MEASURE", "device_selection": "PRESCRIBE",
    "fact_recall": "KNOW", "finding_interpretation": "INTERPRET",
    "functional_goal_decision": "DECIDE", "intervention_selection": "PRESCRIBE",
    "prognosis_prediction": "PREDICT", "safety_priority": "DECIDE",
}
NEAR_THRESHOLD = 0.65
START_Q = 1750
END_Q = 1761
BASE_END = 1749
TARGET_VERSION = "2026-09-b14"
LETTERS = "ABCDE"
QID_PATTERN = r"^Q(?:[1-9]|[1-9][0-9]{1,2}|1[0-6][0-9]{2}|17(?:[0-5][0-9]|6[01]))$"


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def file_fingerprint(path):
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def normalize(stem):
    return re.sub(r"[^\w]", "", unicodedata.normalize("NFKC", stem)).lower()


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                    separators=(",", ":")).encode("utf-8")).hexdigest()


def draft_fingerprint(draft):
    return fingerprint({key: value for key, value in draft.items() if key != "reviewed_sha256"})


def _choice_map(values):
    result = {}
    for index, letter in enumerate(LETTERS, start=1):
        value = values.get(str(index), values.get(letter))
        if value is None:
            raise ValueError(f"missing choice {index}/{letter}")
        result[letter] = str(value)
    return result


def _correct_letters(values):
    result = []
    for value in values:
        text = str(value)
        if text in LETTERS:
            result.append(text)
        elif text.isdigit() and 1 <= int(text) <= 5:
            result.append(LETTERS[int(text) - 1])
        else:
            raise ValueError(f"unsupported correct choice {text}")
    return result


def build_report(payload=None, bank_dir=BANK):
    payload = read(STAGING) if payload is None else payload
    errors, rows = [], []

    def check(condition, message):
        if not condition:
            errors.append(message)

    check(payload.get("status") == "staging_only", "scope: staging_only required")
    for key in ("q_ids_reserved", "production_write", "db_write"):
        check(payload.get(key) is False, f"scope: {key} must be false")

    stores = {name: read(bank_dir / f"{name}.json") for name in STORES}
    maps = {name: {r["id"]: r for r in records} for name, records in stores.items()}
    manifest = read(bank_dir / "bank_manifest.json")
    schema = read(bank_dir / "schema/question_bank_schema_v1.json")
    expected_batch_ids = [f"Q{n}" for n in range(START_Q, END_Q + 1)]
    integrated_count = sum(qid in maps["questions"] for qid in expected_batch_ids)
    check(integrated_count in (0, 12), f"partial formal integration detected: {integrated_count}/12")
    integrated = integrated_count == 12

    hashes = payload.get("formal_input_sha256", {})
    check(payload.get("formal_hash_format") == "sha256-lf-normalized-v1", "formal hash format invalid")
    check(set(hashes) == set(PROTECTED), "formal snapshot: incomplete protected files")
    hash_names = IMMUTABLE_AFTER_INTEGRATION if integrated else PROTECTED
    for name in hash_names:
        check(hashes.get(name) == file_fingerprint(bank_dir / name),
              f"formal snapshot changed: {name}; re-audit required")

    expected_end = END_Q if integrated else BASE_END
    check(manifest["question_count"] == expected_end, "manifest: unexpected question_count")
    check(manifest["last_question_number"] == expected_end, "manifest: unexpected last_question_number")
    if integrated:
        check(manifest.get("bank_version") == TARGET_VERSION, "manifest: unexpected Batch02 version")
        check(schema["$defs"]["qid"]["pattern"] == QID_PATTERN, "schema: QID pattern mismatch")
        for name in STORES:
            check(schema["properties"][name].get("minItems") == END_Q, f"schema: {name} minItems mismatch")
            check(schema["properties"][name].get("maxItems") == END_Q, f"schema: {name} maxItems mismatch")

    expected = [f"Q{n}" for n in range(manifest["first_question_number"],
                                      manifest["last_question_number"] + 1)]
    check(len(expected) == manifest["question_count"], "manifest: range/count mismatch")
    for name, records in stores.items():
        check([r["id"] for r in records] == expected, f"{name}: four-store ID order/count mismatch")

    registry = {r["knowledge_node_id"]: r for r in read(bank_dir / "knowledge_nodes.json")}
    groups = defaultdict(set)
    for tag in stores["question_tags"]:
        groups[canonical(tag["knowledge_node_id"])].add(tag["id"])
    batch01_nodes = {canonical(maps["question_tags"][f"Q{n}"]["knowledge_node_id"])
                     for n in range(1738, 1750)}

    drafts = payload.get("drafts", [])
    accepted = [d for d in drafts if d.get("status") == "accepted"]
    check(len(accepted) == 12, "accepted count must be 12")
    check(len({d.get("draft_id") for d in drafts}) == len(drafts), "duplicate draft ID")
    targets = [canonical(d.get("target_node_id", "")) for d in accepted]
    check(len(set(targets)) == len(targets), "duplicate accepted canonical target")
    formal_stems = {r["id"]: normalize(r["question_text"]) for r in stores["questions"]}
    exact_formal, exact_candidate = [], []

    for offset, d in enumerate(accepted):
        did, node = d.get("draft_id", "?"), d.get("target_node_id", "")
        prefix = f"{did}: "
        expected_qid = f"Q{START_Q + offset}"
        check(re.fullmatch(r"B02-\d{2}", did) is not None, prefix + "invalid draft ID")
        check(not any(k in d for k in ("id", "qid", "q_id", "question_id", "reserved_qid",
                                      "new_question_id", "management_code")), prefix + "Q ID allocation forbidden")
        check(node in registry, prefix + "target Node missing")
        cn = canonical(node)
        check(cn in registry and d.get("target_canonical_node_id") == cn,
              prefix + "canonical resolution mismatch")
        check(cn not in batch01_nodes and cn != canonical("KN0779"), prefix + "excluded Node")

        refs = d.get("reference_question_ids", [])
        if len(refs) != 1 or not all(refs[0] in m for m in maps.values()):
            errors.append(prefix + "reference absent from four stores or not singular")
            continue
        ref = refs[0]
        expected_node_qids = [ref, expected_qid] if integrated else [ref]
        expected_state = "confirmed_shared" if integrated else "singleton_initial"
        expected_group = set(expected_node_qids)
        check(d.get("expected_target_state") == "singleton", prefix + "target staging state contract changed")
        check(groups.get(cn) == expected_group,
              prefix + ("target not canonical integrated pair" if integrated else "target not canonical singleton"))
        if node in registry:
            check(registry[node]["status"] == expected_state,
                  prefix + ("registry state not confirmed_shared" if integrated else "registry state not singleton"))
            check(registry[node].get("question_ids") == expected_node_qids, prefix + "Node/reference registry mismatch")

        tag, question = maps["question_tags"][ref], maps["questions"][ref]
        check(tag["knowledge_node_id"] == node, prefix + "Node/reference registry mismatch")
        snapshot = {k: tag[k] for k in ("task", "primary_ability", "level", "safety")}
        snapshot["question_text"] = question["question_text"]
        check(d.get("reference_snapshot") == snapshot, prefix + "reference snapshot stale")
        check((d.get("proposed_category_large"), d.get("proposed_category_small")) ==
              (question["category_large"], question["category_small"]), prefix + "category mismatch")
        check(d.get("source") == "original", prefix + "source must be original")
        check(d.get("proposed_task") in TASK_PRIMARY and
              TASK_PRIMARY.get(d.get("proposed_task")) == d.get("primary_ability"),
              prefix + "task/ability mismatch")
        check(d.get("secondary_ability") is None or
              d.get("secondary_ability") in set(TASK_PRIMARY.values()) - {d.get("primary_ability")},
              prefix + "secondary ability invalid")
        check(d.get("level") in (1, 2, 3, 4), prefix + "level invalid")
        check(d.get("safety") in ("none", "moderate", "critical"), prefix + "safety invalid")
        check(d.get("proposed_task") != "safety_priority" or d.get("safety") != "none",
              prefix + "safety task lacks safety tag")
        check((d.get("proposed_task"), d.get("primary_ability")) !=
              (tag["task"], tag["primary_ability"]), prefix + "same metadata demand")

        choices, reasons = d.get("choices", {}), d.get("choice_explanations", {})
        choices_valid = (
            isinstance(choices, dict) and isinstance(reasons, dict) and
            set(choices) == set(reasons) == set("12345") and
            all(isinstance(v, str) and v.strip() for v in [*choices.values(), *reasons.values()])
        )
        check(choices_valid, prefix + "five choices and reasons required")
        check(isinstance(choices, dict) and
              len({normalize(v) for v in choices.values() if isinstance(v, str)}) == 5,
              prefix + "duplicate choice text")
        answer = d.get("correct_choices", [])
        answer_valid = (
            isinstance(answer, list) and len(answer) == 1 and
            isinstance(choices, dict) and str(answer[0]) in choices and str(answer[0]) in "12345"
        )
        check(answer_valid, prefix + "single best answer required")
        check(bool(d.get("explanation")) and bool(d.get("clinical_intent")), prefix + "rationale missing")
        stem = d.get("question_text", "")
        check(isinstance(stem, str) and 0 < len(stem) <= 300, prefix + "stem length outside batch limit")
        norm = normalize(stem)

        excluded = {expected_qid} if integrated else set()
        comparison_stems = {qid: text for qid, text in formal_stems.items() if qid not in excluded}
        ranked = sorted(((SequenceMatcher(None, norm, text, autojunk=False).ratio(), qid)
                         for qid, text in comparison_stems.items()), reverse=True)
        duplicates = [qid for qid, text in comparison_stems.items() if text == norm]
        exact_formal.extend((did, qid) for qid in duplicates)
        check(not duplicates, prefix + "exact formal duplicate")

        review = d.get("semantic_review", {})
        check(review.get("decision") == "accepted", prefix + "semantic decision missing")
        for key in ("reference_demand", "candidate_demand", "why_not_same_demand", "reviewer", "reviewed_on"):
            check(bool(review.get(key)), prefix + f"semantic review missing {key}")
        check(review.get("reference_demand") != review.get("candidate_demand"), prefix + "same semantic demand")
        for related in review.get("related_formal_questions", []):
            check(related.get("qid") in maps["questions"] and bool(related.get("difference")),
                  prefix + "related semantic evidence invalid")
        check(d.get("reviewed_sha256") == draft_fingerprint(d), prefix + "content changed after semantic review")
        check(bool(d.get("evidence")) and all(e.get("url", "").startswith("https://") and
              e.get("support") for e in d.get("evidence", [])), prefix + "medical sources missing")
        check(not ranked or ranked[0][0] < NEAR_THRESHOLD, prefix + "near formal stem requires revision/review")

        if integrated:
            for name in STORES:
                check(expected_qid in maps[name], prefix + f"{expected_qid} missing from {name}")
            if all(expected_qid in maps[name] for name in STORES):
                new_question = maps["questions"][expected_qid]
                new_answer = maps["answers"][expected_qid]
                new_explanation = maps["explanations"][expected_qid]
                new_tag = maps["question_tags"][expected_qid]
                check(new_question.get("question_text") == d["question_text"], prefix + "formal stem differs from staging")
                if choices_valid:
                    expected_choices = _choice_map(d["choices"])
                    check(new_question.get("choices") == expected_choices, prefix + "formal choices differ from staging")
                check(new_question.get("category_large") == d["proposed_category_large"] and
                      new_question.get("category_small") == d["proposed_category_small"], prefix + "formal category differs from staging")
                check(new_question.get("source") == "O", prefix + "formal question source mismatch")
                if answer_valid:
                    expected_correct = _correct_letters(d["correct_choices"])
                    check(new_answer.get("display_answer") == expected_correct[0] and
                          new_answer.get("accepted_answer_sets") == [expected_correct] and
                          new_answer.get("answer_basis") == "LT_original", prefix + "formal answer differs from staging")
                if choices_valid:
                    check(new_explanation.get("explanation") == d["explanation"] and
                          new_explanation.get("choice_explanations") == _choice_map(d["choice_explanations"]),
                          prefix + "formal explanation differs from staging")
                expected_tag = {
                    "knowledge_node_id": node,
                    "task": d["proposed_task"],
                    "primary_ability": d["primary_ability"],
                    "secondary_ability": d.get("secondary_ability"),
                    "level": d["level"],
                    "safety": d["safety"],
                    "source": "original",
                }
                for key, value in expected_tag.items():
                    check(new_tag.get(key) == value, prefix + f"formal tag {key} differs from staging")

        rows.append({"draft_id": did, "target_node_id": node, "reference_qid": ref,
                     "expected_integrated_qid": expected_qid, "integrated": integrated,
                     "reference_snapshot": snapshot, "candidate_task": d["proposed_task"],
                     "candidate_ability": d["primary_ability"], "candidate_level": d["level"],
                     "candidate_safety": d["safety"], "nearest_formal": [
                         {"qid": qid, "similarity": round(score, 6)} for score, qid in ranked[:3]]})

    pair_max = 0.0
    for left, right in combinations(accepted, 2):
        a, b = normalize(left["question_text"]), normalize(right["question_text"])
        pair = (left["draft_id"], right["draft_id"])
        if a == b:
            exact_candidate.append(pair)
            errors.append(f"{pair}: exact candidate duplicate")
        score = SequenceMatcher(None, a, b, autojunk=False).ratio()
        pair_max = max(pair_max, score)
        check(score < NEAR_THRESHOLD, f"{pair}: near candidate duplicate requires review")

    return {"accepted_count": len(accepted), "unique_targets": len(set(targets)),
            "integrated_count": integrated_count, "lifecycle": "integrated" if integrated else "staging",
            "formal_count": manifest["question_count"], "canonical_singletons": sum(len(v) == 1 for v in groups.values()),
            "excluded_batch01_nodes": sorted(batch01_nodes), "hard_errors": errors,
            "exact_formal_duplicates": exact_formal, "exact_candidate_duplicates": exact_candidate,
            "near_threshold": NEAR_THRESHOLD, "max_candidate_similarity": round(pair_max, 6),
            "category_counts": dict(Counter(d["proposed_category_small"] for d in accepted)),
            "task_counts": dict(Counter(d["proposed_task"] for d in accepted)),
            "safety_counts": dict(Counter(d["safety"] for d in accepted)), "rows": rows,
            "semantic_limit": "Editorial review plus content seal; not an automated proof of clinical novelty."}


def main():
    report = build_report()
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if report["hard_errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())