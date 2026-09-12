import json
from collections import defaultdict

import pytest

from knowledge_node_canonical import canonicalize_knowledge_node_id
from question_bank import CATEGORY_NAMES, get_category_small, get_question_tag, question_ids


def test_emit_static_pt_field_map_for_one_off_audit():
    questions_by_field = defaultdict(list)
    nodes_by_field = defaultdict(set)
    for qid in question_ids():
        field_id = get_category_small(qid)
        node_id = canonicalize_knowledge_node_id(get_question_tag(qid)["knowledge_node_id"])
        questions_by_field[field_id].append(qid)
        nodes_by_field[field_id].add(node_id)

    payload = {
        str(field_id): {
            "name": CATEGORY_NAMES[field_id],
            "question_count": len(questions_by_field[field_id]),
            "canonical_node_count": len(nodes_by_field[field_id]),
            "qids": questions_by_field[field_id],
            "nodes": sorted(nodes_by_field[field_id]),
        }
        for field_id in sorted(CATEGORY_NAMES)
    }
    # Deliberately fail only on this temporary audit branch so Actions exposes
    # the static mapping in the job log. This branch is never merged.
    pytest.fail("PT18_AUDIT=" + json.dumps(payload, ensure_ascii=False, separators=(",", ":")))
