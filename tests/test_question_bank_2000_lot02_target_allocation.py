from reports.question_bank_2000_lot02_targets_v01 import _solve_slot_split


def inventory(singletons, multis):
    return {
        category: {
            "singleton": [None] * singletons[category],
            "multi": [None] * multis[category],
        }
        for category in singletons
    }


def test_inventory_aware_split_moves_unavailable_c12_multi_without_changing_global_quotas():
    singletons = {8: 20, 9: 20, 11: 20, 12: 20, 14: 20, 16: 20, 17: 20, 18: 20}
    multis = {8: 20, 9: 20, 11: 20, 12: 0, 14: 20, 16: 20, 17: 20, 18: 20}
    split = _solve_slot_split(inventory(singletons, multis))
    assert split[12]["multi"] == 0
    assert split[12]["singleton"] == 4
    assert sum(row["singleton"] for row in split.values()) == 32
    assert sum(row["multi"] for row in split.values()) == 12
    assert sum(row["new"] for row in split.values()) == 4
    assert {c: row["singleton"] + row["multi"] + row["new"] for c, row in split.items()} == {
        8: 8, 9: 6, 11: 5, 12: 5, 14: 4, 16: 5, 17: 7, 18: 8,
    }


def test_inventory_aware_split_fails_when_category_cannot_supply_required_existing_nodes():
    singletons = {8: 20, 9: 20, 11: 20, 12: 3, 14: 20, 16: 20, 17: 20, 18: 20}
    multis = {8: 20, 9: 20, 11: 20, 12: 0, 14: 20, 16: 20, 17: 20, 18: 20}
    try:
        _solve_slot_split(inventory(singletons, multis))
    except ValueError as exc:
        assert "category 12 lacks total existing-Node inventory" in str(exc)
    else:
        raise AssertionError("expected fail-closed inventory error")
