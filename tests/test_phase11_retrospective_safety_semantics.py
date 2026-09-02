from phase11_retrospective_shadow_audit import _safety_miss_flags


def _profile(critical):
    return {"critical_safety_unresolved_count": critical}


def test_shadow_safety_weaker_baseline_is_baseline_miss_not_phase11_miss():
    flags = _safety_miss_flags(
        {"reason_code": "safety_repair", "target_field": "内科学"},
        {"内科学": _profile(1), "小児学": _profile(0)},
        "小児学",
    )
    assert flags["phase11_critical_safety_miss_candidate"] is False
    assert flags["baseline_stronger_safety_miss_candidate"] is True


def test_both_targets_have_j1_safety_is_not_a_baseline_miss():
    flags = _safety_miss_flags(
        {"reason_code": "safety_repair", "target_field": "内科学"},
        {"内科学": _profile(1), "小児学": _profile(1)},
        "小児学",
    )
    assert flags["phase11_critical_safety_miss_candidate"] is False
    assert flags["baseline_stronger_safety_miss_candidate"] is False


def test_unresolved_critical_exists_but_shadow_is_not_safety_is_phase11_miss():
    flags = _safety_miss_flags(
        {"reason_code": "confident_wrong_cluster", "target_field": "小児学"},
        {"内科学": _profile(1), "小児学": _profile(0)},
        "小児学",
    )
    assert flags["phase11_critical_safety_miss_candidate"] is True
    assert flags["baseline_stronger_safety_miss_candidate"] is False


def test_no_unresolved_critical_means_no_miss_flags():
    flags = _safety_miss_flags(
        {"reason_code": "maintenance_only", "target_field": None},
        {"内科学": _profile(0), "小児学": _profile(0)},
        "小児学",
    )
    assert flags["phase11_critical_safety_miss_candidate"] is False
    assert flags["baseline_stronger_safety_miss_candidate"] is False
