from judgment_shadow import build_shadow_comparison


def test_targetless_maintenance_is_consistent_without_profile():
    comparison = build_shadow_comparison(
        {"phase": "analysis", "recommended_study": [("内科学", 10)]},
        {"target_field": None, "reason_code": "maintenance_only"},
        {"内科学": {"reason_rank": 7, "strongest_reason_code": "maintenance_only"}},
    )
    assert comparison["shadow_target"] is None
    assert comparison["shadow_target_formal_evidence"] is None
    assert comparison["shadow_reason_profile_consistent"] is True


def test_targeted_reason_without_profile_remains_inconsistent():
    comparison = build_shadow_comparison(
        {"phase": "analysis", "recommended_study": [("内科学", 10)]},
        {"target_field": "神経学", "reason_code": "confident_wrong_cluster"},
        {"内科学": {"reason_rank": 5, "strongest_reason_code": "insufficient_coverage"}},
    )
    assert comparison["shadow_reason_profile_consistent"] is False


def test_targeted_matching_profile_remains_consistent():
    comparison = build_shadow_comparison(
        {"phase": "analysis", "recommended_study": [("内科学", 10)]},
        {"target_field": "神経学", "reason_code": "confident_wrong_cluster"},
        {
            "内科学": {"reason_rank": 5, "strongest_reason_code": "insufficient_coverage"},
            "神経学": {"reason_rank": 2, "strongest_reason_code": "confident_wrong_cluster"},
        },
    )
    assert comparison["shadow_reason_profile_consistent"] is True
