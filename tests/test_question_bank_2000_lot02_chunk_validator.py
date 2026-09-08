import copy

from reports.question_bank_2000_lot02_chunk_validate import build_report


def draft(index: int, *, slot="singleton_second"):
    row = {
        "draft_id": f"L02-C8-S{index:02d}",
        "status": "accepted",
        "slot_type": slot,
        "target_node_id": "KN0001" if slot != "new_node" else None,
        "target_node_label": "test node",
        "reference_question_ids": ["Q1"] if slot != "new_node" else [],
        "existing_demands": [{"task": "fact_recall", "primary_ability": "KNOW"}] if slot != "new_node" else [],
        "proposed_category_small": 8,
        "source": "original",
        "question_text": f"症例{index}について最も適切なのはどれか。",
        "choices": {str(i): f"選択肢{index}-{i}" for i in range(1, 6)},
        "correct_choices": ["1"],
        "explanation": "正答理由。",
        "choice_explanations": {str(i): f"理由{index}-{i}" for i in range(1, 6)},
        "proposed_task": "finding_interpretation",
        "primary_ability": "INTERPRET",
        "secondary_ability": None,
        "level": 2,
        "safety": "none",
        "clinical_intent": "臨床所見を統合する。",
        "semantic_review": {
            "reference_demand": "fact_recall/KNOW",
            "candidate_demand": "finding_interpretation/INTERPRET",
            "why_not_same_demand": "知識再生ではなく所見統合を要求する。",
            "related_formal_questions": [{"qid": "Q1", "relation": "same Node"}],
            "decision": "accepted",
            "reviewer": "AI review; not human expert",
            "reviewed_on": "2026-09-09",
            "expert_signoff": False,
        },
        "evidence": [{"url": "https://example.org/evidence", "support": "test evidence"}],
        "reviewed_sha256": "",
    }
    if slot == "new_node":
        row["draft_id"] = f"L02-C8-N{index:02d}"
        row["new_node_collision_review"] = {
            "decision": "accepted_new_node",
            "why_existing_nodes_insufficient": "既存Nodeと意味上重ならないことを確認した。",
        }
    return row


def payload():
    return {
        "lot": "question_bank_2000_production_lot02_v01",
        "chunk": 1,
        "chunk_count": 6,
        "status": "completed_chunk",
        "formal_baseline": "Q1-Q1809",
        "q_ids_reserved": False,
        "production_write": False,
        "db_write": False,
        "drafts": [draft(i) for i in range(1, 9)],
    }


def test_valid_synthetic_chunk_passes_local_completeness_contract():
    report = build_report(payload())
    assert report["hard_errors"] == []
    assert report["warnings"] == []
    assert report["draft_count"] == 8


def test_chunk_validator_rejects_formal_qid_allocation():
    data = payload()
    data["drafts"][0]["question_id"] = "Q1810"
    report = build_report(data)
    assert any("formal Q ID allocation forbidden" in error for error in report["hard_errors"])


def test_chunk_validator_rejects_existing_demand_reuse():
    data = payload()
    data["drafts"][0]["proposed_task"] = "fact_recall"
    data["drafts"][0]["primary_ability"] = "KNOW"
    report = build_report(data)
    assert any("candidate demand duplicates existing Node demand" in error for error in report["hard_errors"])


def test_chunk_validator_rejects_exact_duplicate_stems_inside_chunk():
    data = payload()
    data["drafts"][1]["question_text"] = data["drafts"][0]["question_text"]
    report = build_report(data)
    assert any("exact duplicate stems inside chunk" in error for error in report["hard_errors"])


def test_new_node_requires_collision_rationale_key_used_by_final_contract():
    data = payload()
    data["drafts"][0] = draft(1, slot="new_node")
    assert build_report(data)["hard_errors"] == []
    broken = copy.deepcopy(data)
    broken["drafts"][0]["new_node_collision_review"].pop("why_existing_nodes_insufficient")
    report = build_report(broken)
    assert any("new Node collision rationale required" in error for error in report["hard_errors"])
