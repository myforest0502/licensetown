import json
import re
from collections import Counter, defaultdict
from difflib import SequenceMatcher
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BANK = ROOT / "data" / "question_bank"


def _load(name):
    return json.loads((BANK / name).read_text(encoding="utf-8-sig"))


def _norm(value):
    text = str(value or "").lower()
    text = re.sub(r"\s+", "", text)
    return re.sub(r"[、。,.，．・:：;；!?！？()（）\[\]【】「」『』<>＜＞\-―ー]", "", text)


def _stem(q):
    return str(q.get("question_text") or q.get("question") or q.get("stem") or "")


def _choice_signature(q):
    choices = q.get("choices") or q.get("options") or {}
    if isinstance(choices, dict):
        def order_key(item):
            key = str(item[0])
            return (0, int(key)) if key.isdigit() else (1, key)
        return tuple(_norm(v) for _, v in sorted(choices.items(), key=order_key))
    if isinstance(choices, list):
        return tuple(_norm(x.get("text") if isinstance(x, dict) else x) for x in choices)
    return ()


def test_q2000_final_quality_ci_probe():
    questions = _load("questions.json")
    answers = _load("answers.json")
    explanations = _load("explanations.json")
    tags = _load("question_tags.json")
    nodes = _load("knowledge_nodes.json")
    manifest = _load("bank_manifest.json")

    expected = [f"Q{i}" for i in range(1, 2001)]
    expected_set = set(expected)
    blockers = []
    stores = {"questions": questions, "answers": answers, "explanations": explanations, "tags": tags}
    for name, rows in stores.items():
        ids = [str(r.get("id", "")) for r in rows]
        c = Counter(ids)
        dups = sorted(k for k, v in c.items() if k and v > 1)
        missing = sorted(expected_set - set(ids), key=lambda x: int(x[1:]))
        extra = sorted(set(ids) - expected_set)
        if len(ids) != 2000 or dups or missing or extra:
            blockers.append({"type": "store_id_integrity", "store": name, "count": len(ids), "duplicates": dups, "missing": missing, "extra": extra})

    if not (manifest.get("first_question_number") == 1 and manifest.get("last_question_number") == 2000 and manifest.get("question_count") == 2000):
        blockers.append({"type": "manifest", "manifest": manifest})

    qmap = {r["id"]: r for r in questions}
    amap = {r["id"]: r for r in answers}
    emap = {r["id"]: r for r in explanations}

    normalized_stem = defaultdict(list)
    exact_item = defaultdict(list)
    editorial = defaultdict(list)
    for qid in expected:
        q = qmap[qid]
        a = amap[qid]
        e = emap[qid]
        stem = _stem(q).strip()
        stem_norm = _norm(stem)
        normalized_stem[stem_norm].append(qid)
        exact_item[(stem_norm, _choice_signature(q))].append(qid)
        if not stem:
            blockers.append({"type": "empty_stem", "id": qid})
        elif len(stem) < 12 or len(stem) > 450:
            editorial["stem_length"].append({"id": qid, "length": len(stem), "stem": stem})
        if re.search(r"(?:TODO|TBD|XXX|PLACEHOLDER|未作成|仮問題)", stem, re.I):
            editorial["placeholder_like_stem"].append(qid)
        if not (a.get("accepted_answer_sets") or a.get("display_answer") or a.get("answer") or a.get("correct_answer")):
            blockers.append({"type": "answer_missing", "id": qid})
        explanation = str(e.get("explanation") or "").strip()
        if not explanation:
            blockers.append({"type": "missing_explanation", "id": qid})
        elif len(explanation) < 15 or len(explanation) > 1200:
            editorial["explanation_length"].append({"id": qid, "length": len(explanation), "explanation": explanation})
        ce = e.get("choice_explanations")
        if not isinstance(ce, dict) or len(ce) < 2:
            blockers.append({"type": "choice_explanations_missing", "id": qid})

    same_stem = [sorted(v, key=lambda x: int(x[1:])) for k, v in normalized_stem.items() if k and len(v) > 1]
    full_dups = [sorted(v, key=lambda x: int(x[1:])) for (stem, choices), v in exact_item.items() if stem and choices and len(v) > 1]
    full_dups.sort(key=lambda g: int(g[0][1:]))
    if full_dups:
        blockers.append({"type": "exact_duplicate_items", "groups": full_dups})

    same_stem_different_choices = [g for g in same_stem if not any(set(g).issubset(set(d)) for d in full_dups)]

    by_category = defaultdict(list)
    for qid, q in qmap.items():
        n = _norm(_stem(q))
        if n:
            by_category[str(q.get("category_small"))].append((qid, n))
    near = []
    for category, rows in by_category.items():
        rows.sort(key=lambda x: len(x[1]))
        for i, (q1, s1) in enumerate(rows):
            l1 = len(s1)
            for q2, s2 in rows[i + 1:]:
                l2 = len(s2)
                if l2 > max(l1 + 20, int(l1 * 1.25)):
                    break
                if min(l1, l2) / max(l1, l2) < 0.80:
                    continue
                score = SequenceMatcher(None, s1, s2, autojunk=False).ratio()
                if score >= 0.90:
                    near.append({
                        "q1": q1,
                        "q2": q2,
                        "category": category,
                        "similarity": round(score, 4),
                        "stem1": _stem(qmap[q1]),
                        "stem2": _stem(qmap[q2]),
                    })
    near.sort(key=lambda x: x["similarity"], reverse=True)

    node_ids = {str(n.get("knowledge_node_id")) for n in nodes if n.get("knowledge_node_id")}
    tag_node_ids = {str(t.get("knowledge_node_id")) for t in tags if t.get("knowledge_node_id")}
    if tag_node_ids - node_ids:
        blockers.append({"type": "tag_node_reference_missing", "nodes": sorted(tag_node_ids - node_ids)})
    duplicate_labels = defaultdict(list)
    bad_node_qrefs = []
    for n in nodes:
        nid = str(n.get("knowledge_node_id") or "")
        bad = sorted(set(str(x) for x in (n.get("question_ids") or [])) - expected_set)
        if bad:
            bad_node_qrefs.append({"node": nid, "bad_question_ids": bad})
        label = _norm(n.get("label"))
        if label:
            duplicate_labels[label].append(nid)
    if bad_node_qrefs:
        blockers.append({"type": "node_question_reference_missing", "items": bad_node_qrefs})
    duplicate_node_labels = [v for v in duplicate_labels.values() if len(v) > 1]

    summary = {
        "bank_version": manifest.get("bank_version"),
        "question_count": len(questions),
        "blocker_count": len(blockers),
        "blockers": blockers,
        "same_stem_group_count": len(same_stem),
        "same_stem_different_choices_count": len(same_stem_different_choices),
        "exact_duplicate_item_count": len(full_dups),
        "exact_duplicate_items": full_dups,
        "editorial": editorial,
        "near_duplicate_count": len(near),
        "near_duplicates": near,
        "duplicate_node_label_count": len(duplicate_node_labels),
        "duplicate_node_label_candidates": duplicate_node_labels[:100],
    }
    print("Q2000_REVIEW_CANDIDATES=" + json.dumps(summary, ensure_ascii=False, sort_keys=True))
    assert blockers == []
