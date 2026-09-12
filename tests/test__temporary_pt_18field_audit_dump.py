from collections import defaultdict

import pytest

from question_bank import CATEGORY_NAMES, get_category_small, question_ids


def test_emit_static_pt_field_map_for_one_off_audit():
    questions_by_field = defaultdict(list)
    for qid in question_ids():
        questions_by_field[get_category_small(qid)].append(qid)

    clauses = []
    for field_id in sorted(CATEGORY_NAMES):
        quoted = ",".join(f"'{qid}'" for qid in questions_by_field[field_id])
        clauses.append(f"WHEN question_id IN ({quoted}) THEN {field_id}")

    sql_case = "CASE " + " ".join(clauses) + " END"
    # Deliberately fail only on this temporary audit branch so Actions exposes
    # a compact SQL CASE mapping for the one-off production read-only audit.
    pytest.fail("PT18_SQL_CASE=" + sql_case)
