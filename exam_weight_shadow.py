"""Provisional shadow-only Exam Weight model for LicenseTown.

This module intentionally uses only evidence already present in the closed Q1-Q2000
Question Bank. It does NOT claim a complete 20-year longitudinal model because
explicit exam-year provenance is currently available for only a small subset of
past-exam items.

No selector authority, DB writes, learner-facing behavior, or LLM calls.
"""
from __future__ import annotations

from typing import Any

VERSION = "exam_weight_shadow_v0.1_repository_frequency_proxy"
FIELD_COUNT = 18
TOTAL_PAST_EXAM_ITEMS = 1100
TOTAL_ORIGINAL_ITEMS = 900
KNOWN_YEAR_PROVENANCE_ITEMS = 36
YEAR_PROVENANCE_GAP = TOTAL_PAST_EXAM_ITEMS - KNOWN_YEAR_PROVENANCE_ITEMS

FIELD_NAMES = {
    1: "解剖学",
    2: "生理学",
    3: "心理学",
    4: "人間発達学",
    5: "教育学",
    6: "医学概論",
    7: "病理学",
    8: "内科学",
    9: "神経医学",
    10: "精神医学",
    11: "小児学",
    12: "臨床心理学",
    13: "基礎運動学",
    14: "臨床運動学",
    15: "動作分析学",
    16: "運動器",
    17: "理学療法評価各論",
    18: "理学療法治療各論",
}

FIELD_PAST_EXAM_COUNTS = {
    1: 137,
    2: 152,
    3: 15,
    4: 22,
    5: 6,
    6: 34,
    7: 63,
    8: 118,
    9: 65,
    10: 35,
    11: 16,
    12: 13,
    13: 50,
    14: 5,
    15: 25,
    16: 53,
    17: 87,
    18: 204,
}


def field_exam_weight(field_id: int) -> dict[str, Any]:
    """Return a reproducible provisional field weight.

    `past_exam_share` is the field's share of the 1,100 stored past-exam items.
    `relative_weight` is normalized so the 18-field arithmetic mean equals 1.0.
    Full temporal weighting is deliberately disabled until provenance is complete.
    """
    field_id = int(field_id)
    if field_id not in FIELD_PAST_EXAM_COUNTS:
        raise ValueError(f"unknown field_id: {field_id}")
    count = FIELD_PAST_EXAM_COUNTS[field_id]
    share = count / TOTAL_PAST_EXAM_ITEMS
    relative = share / (1.0 / FIELD_COUNT)
    return {
        "version": VERSION,
        "shadow_only": True,
        "selection_authority": False,
        "provisional": True,
        "field_id": field_id,
        "field_name": FIELD_NAMES[field_id],
        "past_exam_count": count,
        "past_exam_share": share,
        "relative_weight": relative,
        "temporal_adjustment_available": False,
        "temporal_adjustment": 1.0,
        "provenance_quality": "aggregate_source_only",
        "known_year_provenance_items": KNOWN_YEAR_PROVENANCE_ITEMS,
        "year_provenance_gap": YEAR_PROVENANCE_GAP,
    }


def exam_weight_bundle() -> dict[str, Any]:
    fields = [field_exam_weight(field_id) for field_id in sorted(FIELD_PAST_EXAM_COUNTS)]
    return {
        "version": VERSION,
        "shadow_only": True,
        "selection_authority": False,
        "provisional": True,
        "method": "repository_past_exam_frequency_proxy",
        "past_exam_items": TOTAL_PAST_EXAM_ITEMS,
        "original_items": TOTAL_ORIGINAL_ITEMS,
        "known_year_provenance_items": KNOWN_YEAR_PROVENANCE_ITEMS,
        "year_provenance_gap": YEAR_PROVENANCE_GAP,
        "temporal_adjustment_available": False,
        "fields": fields,
    }
