import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).parents[1]
BANK = ROOT / "data" / "question_bank"
REPORT = ROOT / "reports" / "question_bank_2000_remaining_allocation_v01.json"
ROSTER = ROOT / "reports" / "question_bank_2000_lot01_targets_v01.json"
TEMPLATE = ROOT / "staging" / "question_bank_2000_lot01_template_v01.json"


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def test_remaining_allocation_balances_to_2000():
    manifest = read(BANK / "bank_manifest.json")
    report = read(REPORT)
    assert manifest["question_count"] == manifest["last_question_number"] == 1809
    assert report["current_formal_count"] == 1809
    assert report["formal_original_added_since_audit"] == 72
    assert report["original_remaining"] == 185
    assert report["past_exam_remaining"] == 6
    assert report["total_remaining"] == 191
    assert report["current_formal_count"] + report["total_remaining"] == 2000
    remaining = report["remaining_original_plan"]
    assert sum(map(int, remaining["category"].values())) == 185
    assert sum(map(int, remaining["task"].values())) == 185
    assert sum(map(int, remaining["level"].values())) == 185
    assert sum(map(int, remaining["node_slot"].values())) == 185
    assert report["used"]["node_slot"] == {
        "multi_reinforcement": 10, "new_node": 4, "singleton_second": 58,
    }
    assert report["used"]["strong_formations"] == 68
    assert report["used"]["weak_or_unproven_formations"] == []


def test_lot01_roster_has_exact_structural_quota_without_reusing_calibration_nodes():
    roster = read(ROSTER)
    targets = roster["existing_node_targets"]
    assert roster["formal_baseline"] == "Q1-Q1761"
    assert len(targets) == len({row["canonical_node_id"] for row in targets}) == 44
    assert Counter(row["slot_type"] for row in targets) == Counter({
        "singleton_second": 32,
        "multi_reinforcement": 12,
    })
    category_existing = Counter(int(row["category_small"]) for row in targets)
    new_slots = Counter(int(row["category_small"]) for row in roster["new_node_reservations"])
    assert category_existing + new_slots == Counter({9: 12, 16: 10, 17: 12, 18: 14})
    assert new_slots == Counter({9: 1, 16: 1, 17: 1, 18: 1})
    for row in targets:
        assert all(int(qid[1:]) <= 1737 for qid in row["question_ids"])
        assert row["canonical_node_id"] != "KN0779"
        if row["slot_type"] == "singleton_second":
            assert len(row["question_ids"]) == 1
        else:
            assert len(row["question_ids"]) > 1


def test_lot01_authoring_template_is_qid_free_and_matches_roster():
    roster = read(ROSTER)
    template = read(TEMPLATE)
    drafts = template["drafts"]
    assert template["status"] == "template_only"
    assert template["formal_baseline"] == "Q1-Q1761"
    assert template["q_ids_reserved"] is False
    assert template["production_write"] is False
    assert template["db_write"] is False
    assert len(drafts) == len({row["draft_id"] for row in drafts}) == 48
    assert Counter(row["slot_type"] for row in drafts) == Counter({
        "singleton_second": 32,
        "multi_reinforcement": 12,
        "new_node": 4,
    })
    roster_ids = {row["lot_target_id"] for row in roster["existing_node_targets"]}
    template_existing = {row["draft_id"] for row in drafts if row["slot_type"] != "new_node"}
    assert template_existing == roster_ids
    for row in drafts:
        forbidden = {"id", "qid", "q_id", "question_id", "reserved_qid", "new_question_id", "management_code"}
        assert not forbidden.intersection(row)
        assert row["status"] == "authoring"
        assert row["source"] == "original"
        assert set(row["choices"]) == set(row["choice_explanations"]) == set("12345")
    new_categories = Counter(int(row["proposed_category_small"]) for row in drafts if row["slot_type"] == "new_node")
    assert new_categories == Counter({9: 1, 16: 1, 17: 1, 18: 1})


def test_lot01_quota_dimensions_are_exact():
    template = read(TEMPLATE)
    quotas = template["quotas"]
    assert sum(map(int, quotas["category"].values())) == 48
    assert sum(map(int, quotas["task"].values())) == 48
    assert sum(map(int, quotas["level"].values())) == 48
    assert sum(map(int, quotas["slot_type"].values())) == 48
    assert quotas["minimum_strong_formations"] == 41
    assert quotas["safety_moderate_or_critical"] == 12
