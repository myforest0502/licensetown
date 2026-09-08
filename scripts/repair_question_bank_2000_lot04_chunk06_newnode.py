"""Replace the rejected Lot04 C1 new-Node draft after formal similarity found Q595.

The original posterior-cord concept was not new: Q595 already asks which nerve
branches from the posterior cord. This patch replaces that draft with a distinct
anatomy Node about the long thoracic nerve roots. No formal Q/Node ID is allocated.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "staging" / "question_bank_2000_lot04_chunks_v01" / "chunk_06.json"
DRAFT_ID = "L04-C1-N01"


def main() -> int:
    payload = json.loads(PATH.read_text(encoding="utf-8-sig"))
    draft = next((d for d in payload["drafts"] if d.get("draft_id") == DRAFT_ID), None)
    if draft is None:
        raise SystemExit(f"missing {DRAFT_ID}")
    if draft.get("slot_type") != "new_node" or int(draft.get("proposed_category_small")) != 1:
        raise SystemExit(f"unexpected target contract for {DRAFT_ID}")

    draft.update({
        "target_node_label": "胸長神経は主にC5・C6・C7神経根から形成され前鋸筋を支配する",
        "title": "胸長神経の神経根",
        "question_text": "前鋸筋を支配する胸長神経を構成する主な神経根の組合せはどれか。",
        "choices": {
            "1": "C5・C6・C7",
            "2": "C1・C2・C3",
            "3": "C3・C4・C5",
            "4": "C7・C8・T1",
            "5": "L2・L3・L4",
        },
        "correct_choices": ["1"],
        "explanation": "胸長神経は腕神経叢の根部で主にC5、C6、C7前枝から形成され、前鋸筋を支配する。胸長神経障害では前鋸筋麻痺により翼状肩甲を生じ得る。",
        "choice_explanations": {
            "1": "○。胸長神経の主要な神経根はC5・C6・C7である。",
            "2": "上位頸神経のみの組合せであり胸長神経の主要根ではない。",
            "3": "C3・C4は胸長神経の典型的構成根ではない。",
            "4": "下位腕神経叢優位の組合せであり胸長神経とは異なる。",
            "5": "腰神経であり胸長神経を形成しない。",
        },
        "proposed_task": "fact_recall",
        "primary_ability": "KNOW",
        "secondary_ability": None,
        "level": 1,
        "safety": "none",
        "clinical_intent": "前鋸筋支配神経の根レベルを解剖学的に理解する。",
        "semantic_review": {
            "reference_demand": "replacement new Node candidate; previous posterior-cord candidate rejected because Q595 was hard-near and semantically overlapping",
            "candidate_demand": "fact_recall/KNOW: 胸長神経を形成する主要神経根を同定する。",
            "why_not_same_demand": "Q595の後神経束終末枝とは異なり、腕神経叢根部から直接生じる胸長神経のC5-C7構成を扱う。",
            "related_formal_questions": [{"qid": "Q595", "relation": "explicitly reviewed previous collision; replacement demand differs"}],
            "decision": "accepted",
            "reviewer": "Aoi/GPT-5.6 Sol medical-structure review (AI; not human expert)",
            "reviewed_on": "2026-09-09",
            "expert_signoff": False,
        },
        "new_node_collision_review": {
            "decision": "accepted_new_node",
            "why_existing_nodes_insufficient": "Repository text search for 胸長神経 C5 C6 C7 前枝 returned no indexed result. Q595 was explicitly rejected as a collision with the prior candidate; bank-wide similarity and label collision gates remain required.",
        },
        "evidence": [{
            "url": "https://www.ncbi.nlm.nih.gov/books/NBK531473/",
            "support": "NCBI StatPearls states that the long thoracic nerve originates from the C5, C6, and C7 rami and innervates serratus anterior.",
        }],
        "reviewed_sha256": "",
        "assignment_status": "replacement_after_formal_similarity_collision",
        "assignment_may_change_if_quotas_preserved": True,
    })
    PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"replaced": DRAFT_ID, "reason": "Q595 hard-near collision", "new_concept": draft["target_node_label"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
