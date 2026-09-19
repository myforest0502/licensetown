from exam_weight_shadow import FIELD_PAST_EXAM_COUNTS, TOTAL_PAST_EXAM_ITEMS, YEAR_PROVENANCE_GAP, exam_weight_bundle, field_exam_weight


def test_inventory_and_shadow_contract():
    assert sum(FIELD_PAST_EXAM_COUNTS.values()) == TOTAL_PAST_EXAM_ITEMS == 1100
    assert YEAR_PROVENANCE_GAP == 1064
    bundle = exam_weight_bundle()
    assert bundle["shadow_only"] is True
    assert bundle["selection_authority"] is False
    assert bundle["provisional"] is True
    assert bundle["temporal_adjustment_available"] is False
    assert len(bundle["fields"]) == 18


def test_relative_weights_are_normalized_and_frequency_based():
    fields = exam_weight_bundle()["fields"]
    assert abs(sum(row["relative_weight"] for row in fields) / 18 - 1.0) < 1e-12
    assert max(fields, key=lambda row: row["relative_weight"])["field_id"] == 18
    assert min(fields, key=lambda row: row["relative_weight"])["field_id"] == 14


def test_temporal_claims_are_disabled_without_full_provenance():
    row = field_exam_weight(8)
    assert row["provenance_quality"] == "aggregate_source_only"
    assert row["temporal_adjustment_available"] is False
    assert row["temporal_adjustment"] == 1.0


def test_frequency_constants_match_formal_repository_records():
    import json
    from collections import Counter
    from pathlib import Path

    bank = Path(__file__).resolve().parents[1] / "licensetown" / "pt" / "data" / "question_bank"
    tags = json.loads((bank / "question_tags.json").read_text(encoding="utf-8-sig"))
    questions = json.loads((bank / "questions.json").read_text(encoding="utf-8-sig"))
    assert len(tags) == len(questions) == 2000
    assert {row["id"] for row in tags} == {f"Q{i}" for i in range(1, 2001)}
    assert Counter(row["source"] for row in tags) == {"original": 900, "past_exam": 1100}
    field_by_id = {row["id"]: int(row["category_small"]) for row in questions}
    assert Counter(field_by_id[row["id"]] for row in tags if row["source"] == "past_exam") == FIELD_PAST_EXAM_COUNTS
