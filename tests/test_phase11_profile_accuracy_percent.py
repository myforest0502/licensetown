from judgment_shadow import _compat_profile_aliases


def test_accuracy_ratio_is_preserved_and_percent_is_added():
    profile = _compat_profile_aliases({"raw_answer_count": 10, "raw_accuracy": 0.8})
    assert profile["accuracy"] == 0.8
    assert profile["accuracy_percent"] == 80.0


def test_none_accuracy_remains_unavailable_for_presentation():
    profile = _compat_profile_aliases({"raw_answer_count": 0, "raw_accuracy": None})
    assert profile["accuracy"] is None
    assert profile["accuracy_percent"] is None
