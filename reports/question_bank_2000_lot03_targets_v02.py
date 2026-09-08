"""Inventory adjustment for Lot03 target selection.

Category 14 has only one eligible existing Node after excluding post-Q1809 supply.
Reserve its second Lot03 question as a new Node and move the prior C15 new-Node
reservation to an existing C15 target. Global 30/13/5 and category totals remain exact.
"""
from reports import question_bank_2000_lot03_targets_v01 as base

base.CATEGORY_SLOT[14] = {"singleton": 1, "multi": 0, "new": 1}
base.CATEGORY_SLOT[15] = {"singleton": 3, "multi": 1, "new": 0}

if __name__ == "__main__":
    raise SystemExit(base.main())
