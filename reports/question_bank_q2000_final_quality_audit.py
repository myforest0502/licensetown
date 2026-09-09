"""Cross-sectional final quality audit for the formal Q1-Q2000 PT Question Bank.

Read-only with respect to formal bank data. The script writes one JSON report under reports/.
It is intentionally conservative: structural/data-integrity failures are blockers; editorial
heuristics are review candidates, not automatic failures.
"""
from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from difflib import SequenceMatcher
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BANK = ROOT / "data" / "question_bank"
OUT = ROOT / "reports" / "question_bank_q2000_final_quality_audit.json"


def load(name: str):
    return json.loads((BANK / name).read_text(encoding="utf-8-sig"))


def norm_text(value) -> str:
    text = str(value or "").lower()
    text = re.sub(r"\s+", "", text)
    text = re.sub(r"[、。,.，．・:：;；!?！？()（）\[\]【】「」『』<>＜＞\-―ー]", "", text)
    return text


def get_stem(q: dict) -> str:
    return str(q.get("question_text") or q.get("question") or q.get("stem") or "")


def choice_keys(q: dict) -> set[str]:
    choices = q.get("choices") or q.get("options") or []
    if isinstance(choices, dict):
        return {str(k) for k in choices}
    if isinstance(choices, list):
        # Formal bank is five-choice. Support both raw strings and keyed objects.
        keys = set()
        for idx, item in enumerate(choices, 1):
            if isinstance(item, dict):
                key = item.get("id") or item.get("key") or item.get("number") or idx
            else:
                key = idx
            keys.add(str(key))
        return keys
    return set()


def accepted_sets(a: dict) -> list[list[str]]:
    raw = a.get("accepted_answer_sets")
    if isinstance(raw, list):
        out = []
        for s in raw:
            if isinstance(s, list):
                out.append([str(x) for x in s])
        if out:
            return out
    display = a.get("display_answer") or a.get("answer") or a.get("correct_answer")
    if display is None:
        return []
    if isinstance(display, list):
        return [[str(x) for x in display]]
    return [[x for x in re.split(r"[^0-9A-Ea-e]+", str(display)) if x]]


def main() -> int:
    questions = load("questions.json")
    answers = load("answers.json")
    explanations = load("explanations.json")
    tags = load("question_tags.json")
    nodes = load("knowledge_nodes.json")
    manifest = load("bank_manifest.json")

    stores = {
        "questions": questions,
        "answers": answers,
        "explanations": explanations,
        "tags": tags,
    }
    ids = {name: [str(r.get("id", "")) for r in rows] for name, rows in stores.items()}
    expected = [f"Q{i}" for i in range(1, 2001)]
    expected_set = set(expected)
    blockers: list[dict] = []
    review: dict[str, list] = defaultdict(list)

    # Fundamental store integrity.
    for name, store_ids in ids.items():
        c = Counter(store_ids)
        dups = sorted(k for k, v in c.items() if k and v > 1)
        missing = sorted(expected_set - set(store_ids), key=lambda x: int(x[1:]))
        extra = sorted(set(store_ids) - expected_set)
        if len(store_ids) != 2000 or dups or missing or extra:
            blockers.append({
                "type": "store_id_integrity",
                "store": name,
                "count": len(store_ids),
                "duplicates": dups,
                "missing": missing,
                "extra": extra,
            })

    if not (
        manifest.get("first_question_number") == 1
        and manifest.get("last_question_number") == 2000
        and manifest.get("question_count") == 2000
    ):
        blockers.append({"type": "manifest", "manifest": manifest})

    qmap = {r["id"]: r for r in questions}
    amap = {r["id"]: r for r in answers}
    emap = {r["id"]: r for r in explanations}
    tmap = {r["id"]: r for r in tags}

    # Distributions requested for the final cross-sectional audit.
    distributions = {}
    for field in ("category_small", "category_large", "source"):
        distributions[field] = dict(sorted(Counter(str(q.get(field)) for q in questions).items()))
    for field in ("task", "level", "safety", "primary_ability", "secondary_ability"):
        distributions[field] = dict(sorted(Counter(str(t.get(field)) for t in tags).items()))

    # Answer / explanation / stem quality heuristics.
    normalized_to_ids = defaultdict(list)
    for qid in expected:
        q = qmap[qid]
        a = amap[qid]
        e = emap[qid]
        stem = get_stem(q).strip()
        norm = norm_text(stem)
        normalized_to_ids[norm].append(qid)
        keys = choice_keys(q)
        sets = accepted_sets(a)
        if not stem:
            blockers.append({"type": "empty_stem", "id": qid})
        elif len(stem) < 12 or len(stem) > 450:
            review["stem_length"].append({"id": qid, "length": len(stem)})
        if re.search(r"(?:TODO|TBD|XXX|PLACEHOLDER|未作成|仮問題)", stem, re.I):
            review["placeholder_like_stem"].append(qid)
        if not keys or len(keys) < 2:
            blockers.append({"type": "choice_shape", "id": qid, "choice_keys": sorted(keys)})
        if not sets or any(not s for s in sets):
            blockers.append({"type": "answer_missing", "id": qid})
        elif keys:
            invalid = sorted({x for s in sets for x in s if x not in keys})
            # Formal choices may be numbered while old records use A-E; only block when
            # no accepted value can be mapped to the actual choice set.
            if invalid and all(not set(s).intersection(keys) for s in sets):
                blockers.append({"type": "answer_outside_choices", "id": qid, "answer_sets": sets, "choice_keys": sorted(keys)})
        explanation = str(e.get("explanation") or "").strip()
        if not explanation:
            blockers.append({"type": "missing_explanation", "id": qid})
        elif len(explanation) < 15 or len(explanation) > 1200:
            review["explanation_length"].append({"id": qid, "length": len(explanation)})
        ce = e.get("choice_explanations")
        if not isinstance(ce, dict) or len(ce) < 2:
            blockers.append({"type": "choice_explanations_missing", "id": qid})
        elif keys:
            missing_ce = sorted(k for k in keys if k not in {str(x) for x in ce})
            # Keep as editorial review because legacy records can use A-E vs 1-5 keys.
            if missing_ce:
                review["choice_explanation_key_mismatch"].append({"id": qid, "missing": missing_ce})

    exact_dups = [sorted(v, key=lambda x: int(x[1:])) for k, v in normalized_to_ids.items() if k and len(v) > 1]
    if exact_dups:
        blockers.append({"type": "exact_duplicate_stems", "groups": exact_dups})

    # High-similarity candidates. Compare within category only and use a length gate;
    # these are sampling targets, not automatic failures.
    by_category = defaultdict(list)
    for qid, q in qmap.items():
        n = norm_text(get_stem(q))
        if n:
            by_category[str(q.get("category_small"))].append((qid, n))
    near = []
    for category, rows in by_category.items():
        rows.sort(key=lambda x: len(x[1]))
        for i, (qid1, s1) in enumerate(rows):
            l1 = len(s1)
            for qid2, s2 in rows[i + 1:]:
                l2 = len(s2)
                if l2 > max(l1 + 20, int(l1 * 1.25)):
                    break
                ratio_len = min(l1, l2) / max(l1, l2)
                if ratio_len < 0.80:
                    continue
                score = SequenceMatcher(None, s1, s2, autojunk=False).ratio()
                if score >= 0.90:
                    near.append({"q1": qid1, "q2": qid2, "category": category, "similarity": round(score, 4)})
    near.sort(key=lambda x: x["similarity"], reverse=True)
    review["near_duplicate_candidates"] = near[:100]

    # Knowledge Node cross-checks.
    node_ids = {str(n.get("knowledge_node_id")) for n in nodes if n.get("knowledge_node_id")}
    tag_node_ids = {str(t.get("knowledge_node_id")) for t in tags if t.get("knowledge_node_id")}
    missing_nodes = sorted(tag_node_ids - node_ids)
    if missing_nodes:
        blockers.append({"type": "tag_node_reference_missing", "nodes": missing_nodes})
    bad_node_qrefs = []
    node_size = Counter()
    node_status = Counter()
    duplicate_node_labels = defaultdict(list)
    for n in nodes:
        nid = str(n.get("knowledge_node_id") or "")
        qrefs = [str(x) for x in (n.get("question_ids") or [])]
        node_size[len(qrefs)] += 1
        node_status[str(n.get("status"))] += 1
        bad = sorted(set(qrefs) - expected_set)
        if bad:
            bad_node_qrefs.append({"node": nid, "bad_question_ids": bad})
        label_norm = norm_text(n.get("label"))
        if label_norm:
            duplicate_node_labels[label_norm].append(nid)
    if bad_node_qrefs:
        blockers.append({"type": "node_question_reference_missing", "items": bad_node_qrefs})
    same_label_nodes = [v for v in duplicate_node_labels.values() if len(v) > 1]
    if same_label_nodes:
        review["duplicate_node_label_candidates"] = same_label_nodes[:100]

    node_summary = {
        "registry_nodes": len(nodes),
        "tag_referenced_nodes": len(tag_node_ids),
        "status": dict(sorted(node_status.items())),
        "singleton_nodes": node_size.get(1, 0),
        "multi_question_nodes": sum(v for k, v in node_size.items() if k > 1),
        "max_questions_per_node": max(node_size, default=0),
        "question_count_histogram": {str(k): v for k, v in sorted(node_size.items())},
    }

    report = {
        "scope": "Q1-Q2000",
        "bank_version": manifest.get("bank_version"),
        "question_count": len(questions),
        "blocker_count": len(blockers),
        "blockers": blockers,
        "distributions": distributions,
        "knowledge_nodes": node_summary,
        "review_candidate_counts": {k: len(v) for k, v in review.items()},
        "review_candidates": dict(review),
        "interpretation": {
            "blockers": "must be zero before PT bank is treated as structurally final",
            "review_candidates": "heuristic sampling targets; human/medical review decides whether changes are required",
        },
    }
    OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "scope": report["scope"],
        "bank_version": report["bank_version"],
        "question_count": report["question_count"],
        "blocker_count": report["blocker_count"],
        "distributions": report["distributions"],
        "knowledge_nodes": report["knowledge_nodes"],
        "review_candidate_counts": report["review_candidate_counts"],
        "top_near_duplicate_candidates": report["review_candidates"].get("near_duplicate_candidates", [])[:20],
    }, ensure_ascii=False, indent=2))
    return 1 if blockers else 0


if __name__ == "__main__":
    raise SystemExit(main())
