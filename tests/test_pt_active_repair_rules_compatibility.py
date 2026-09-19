"""PT rule relocation: import order, results and function globals stay compatible."""
import subprocess
import sys
from pathlib import Path

import pytest


@pytest.mark.parametrize("first", [
    "phase11_active_repair_rules",
    "licensetown.pt.phase11_active_repair_rules",
])
def test_import_order_outputs_globals_and_offline_boundary(first):
    script = f"""
import importlib
import importlib.abc
import sys
class BlockRuntime(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split('.')[0] in {{'database', 'question_bank', 'app', 'wsgi', 'psycopg'}}:
            raise AssertionError(fullname)
sys.meta_path.insert(0, BlockRuntime())
importlib.import_module({first!r})
legacy = importlib.import_module('phase11_active_repair_rules')
pt = importlib.import_module('licensetown.pt.phase11_active_repair_rules')
assert legacy is pt
assert legacy.build_j2_candidates is pt.build_j2_candidates
assert legacy.build_j3_candidates is pt.build_j3_candidates
facts = {{2: {{'active_confident_wrong_repairing_node_count': 2,
              'active_repeated_weakness_node_count': 2}},
         1: {{'active_cross_question_confident_wrong_node_count': 1,
              'active_cross_question_wrong_node_count': 1}}}}
fields = {{1: {{'evaluable_answer_count': 10, 'evaluable_accuracy': 0.5}}}}
for module in (legacy, pt):
    assert [r['field_id'] for r in module.build_j2_candidates(facts, field_records=fields)] == [1, 2]
    assert [r['field_id'] for r in module.build_j3_candidates(facts)] == [1, 2]
    assert module.build_j2_candidates({{}}, field_records={{}}) == []
    assert module.build_j3_candidates({{}}) == []
# Private helper replacement must affect already-imported functions on both paths.
from phase11_active_repair_rules import build_j2_candidates
legacy._evaluable_count = lambda field: 77
assert all(r['evaluable_answer_count'] == 77 for r in pt.build_j2_candidates(facts, field_records=fields))
pt._evaluable_count = lambda field: 88
assert all(r['evaluable_answer_count'] == 88 for r in build_j2_candidates(facts, field_records=fields))
"""
    result = subprocess.run(
        [sys.executable, '-B', '-c', script],
        cwd=Path(__file__).resolve().parents[1], capture_output=True, text=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stdout + result.stderr
