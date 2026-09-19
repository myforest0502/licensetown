"""Legacy import order and global-state compatibility for the PT relocation."""
import subprocess
import sys
from pathlib import Path

import pytest


@pytest.mark.parametrize("first", ["exam_weight_shadow", "licensetown.pt.exam_weight_shadow"])
def test_both_import_orders_share_globals_and_remain_offline(first):
    script = f"""
import importlib
import sys
import importlib.abc
class BlockRuntime(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split('.')[0] in {{'database', 'question_bank', 'app', 'psycopg'}}:
            raise AssertionError(fullname)
sys.meta_path.insert(0, BlockRuntime())
importlib.import_module({first!r})
legacy = importlib.import_module('exam_weight_shadow')
pt = importlib.import_module('licensetown.pt.exam_weight_shadow')
assert legacy is pt
from exam_weight_shadow import field_exam_weight
assert field_exam_weight is pt.field_exam_weight
before = pt.field_exam_weight(1)
legacy.TOTAL_PAST_EXAM_ITEMS = 2200
assert pt.field_exam_weight(1)['past_exam_share'] == before['past_exam_share'] / 2
pt.FIELD_NAMES = {{**pt.FIELD_NAMES, 1: 'patched'}}
assert field_exam_weight(1)['field_name'] == 'patched'
assert legacy.exam_weight_bundle()['selection_authority'] is False
"""
    result = subprocess.run(
        [sys.executable, '-B', '-c', script],
        cwd=Path(__file__).resolve().parents[1], capture_output=True, text=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stdout + result.stderr
